# -*- coding: utf-8 -*-
from collections import OrderedDict
import copy
import io
import os.path
from typing import Any, Dict
import uuid

from chaoslib.extension import merge_extension
from flask import abort, Blueprint, current_app, redirect, render_template, \
    jsonify, request, send_file, session, url_for, Response
from flask_accept import accept, accept_fallback
import shortuuid
import simplejson as json
import yaml
import yamlloader

from chaoshubdashboard.model import db
from chaoshubdashboard.utils import cache, load_user

from ..model import Experiment
from ..services import DashboardService
from ..types import UserClaim

__all__ = ["workspace_experiment_service"]

workspace_experiment_service = Blueprint(
    "workspace_experiment_service", __name__)


@workspace_experiment_service.route('<string:experiment_id>', methods=['GET'])
@accept_fallback
@load_user(allow_anonymous=True)
def index(user_claim: UserClaim, experiment_id: str, org: str, workspace: str):
    return render_template('index.html')


@workspace_experiment_service.route(
    '<string:experiment_id>/schedule', methods=['GET'])
@load_user(allow_anonymous=False)
def schedule(user_claim: UserClaim, experiment_id: str, org: str,
             workspace: str):
    return render_template('index.html')


@workspace_experiment_service.route('<string:experiment_id>', methods=['GET'])
@index.support("application/json", "application/x-yaml")
@load_user(allow_anonymous=True)
def raw(user_claim: UserClaim, experiment_id: str, org: str, workspace: str):
    experiment = load_experiment(user_claim, experiment_id, org, workspace)
    url = url_for(
        "workspace_experiment_service.index", org=org, workspace=workspace,
        experiment_id=experiment_id, _external=True)
    mimetypes = request.headers.get("Accept")
    if "application/json" in mimetypes:
        payload = prepare_raw(experiment, url=url, fmt="json")
        content_type = "application/json"
    elif "application/x-yaml" in mimetypes:
        payload = prepare_raw(experiment, url=url, fmt="yaml")
        content_type = "application/x-yaml"
    else:
        return abort(406)

    return Response(payload, status=200, content_type=content_type)


@workspace_experiment_service.route(
    '<string:experiment_id>/context', methods=['GET'])
@accept("application/json")
@load_user(allow_anonymous=True)
def context(user_claim: UserClaim, experiment_id: str, org: str,
            workspace: str):
    url = url_for(
        "workspace_experiment_service.index", org=org, workspace=workspace,
        experiment_id=experiment_id, _external=True)
    experiment_id = shortuuid.decode(experiment_id)
    experiment = Experiment.query.filter(Experiment.id==experiment_id).first()
    if not experiment:
        return abort(404)

    w = DashboardService.get_user_workspace(user_claim, org, workspace)
    if not w:
        return abort(404)

    if "view" not in w["context"]["acls"]:
        return abort(404)

    e = experiment.to_public_dict()
    e["workspace"] = w
    e["requested_by"] = None
    e["url"] = url

    if user_claim:
        e["requested_by"] = DashboardService.get_user_details(
            user_claim, shortuuid.decode(w["org"]["id"]),
            shortuuid.decode(w["id"]))

    return jsonify(e)


@workspace_experiment_service.route('', methods=['POST'])
@load_user(allow_anonymous=False)
def new(user_claim: UserClaim, org: str, workspace: str):
    w = DashboardService.get_workspace(user_claim, org, workspace)
    if not w:
        return abort(404)

    acls = w["context"]["acls"]
    if "view" not in acls:
        return abort(404)

    if "write" not in acls:
        return abort(404)

    account_id = user_claim["id"]
    details = request.json
    declaration = details.get("file")
    if not declaration:
        title = details.get("title", "").strip()
        if not title:
            return abort(400)

        declaration = {
            "title": title,
            "description": details.get("description")
        }
    else:
        try:
            declaration = json.loads(declaration)
        except json.JSONDecodeError as x:
            current_app.logger.error(
                "Failed to parse uploaded experiment: {}".format(str(x)))
            return abort(404)

    experiment = Experiment(
        shared_ref=uuid.uuid4(),
        account_id=account_id,
        org_id=shortuuid.decode(w["org"]["id"]),
        workspace_id=shortuuid.decode(w["id"]),
        payload=declaration
    )
    db.session.add(experiment)
    db.session.commit()

    current_app.logger.info(account_id)
    DashboardService.push_activity({
        "title": experiment.payload["title"],
        "account_id": user_claim["short_id"],
        "type": "experiment",
        "info": "created",
        "org_id": w["org"]["id"],
        "workspace_id": w["id"],
        "experiment_id": shortuuid.encode(experiment.id),
        "visibility": "anonymous"
    })

    w.pop("context", None)
    return jsonify({
        "id": shortuuid.encode(experiment.id),
        "workspace": w
    }), 201


@workspace_experiment_service.route('<string:experiment_id>/download/json',
                                    methods=['GET'])
@load_user(allow_anonymous=True)
def download_json(user_claim: UserClaim, experiment_id: str,
                  org: str, workspace: str):
    return download(user_claim, experiment_id, org, workspace, 'json')


@workspace_experiment_service.route('<string:experiment_id>/download/yaml',
                                    methods=['GET'])
@load_user(allow_anonymous=True)
def download_yaml(user_claim: UserClaim, experiment_id: str,
                  org: str, workspace: str):
    return download(
        user_claim, experiment_id, org, workspace, 'yaml', 'experiment.yaml',
        'application/x-yaml')


def load_experiment(user_claim: UserClaim, experiment_id: str, org: str,
                    workspace: str) -> Experiment:
    experiment_id = shortuuid.decode(experiment_id)
    experiment = Experiment.query.filter(Experiment.id==experiment_id).first()
    if not experiment:
        raise abort(404)

    w = DashboardService.get_workspace(user_claim, org, workspace)
    if not w:
        raise abort(404)

    if "view" not in w["context"]["acls"]:
        raise abort(404)

    return experiment


def prepare_raw(experiment: Experiment, url: str, fmt: str = 'json') -> str:
    exp = json.loads(json.dumps(experiment.payload))

    # set the experiment id in the payload so that we know where to attach
    # executions
    exp_id = shortuuid.encode(experiment.id)
    merge_extension(exp, {
        "name": "chaoshub",
        "self": url,
        "experiment": exp_id
    })

    if fmt == 'json':
        payload = json.dumps(exp, indent=2)
    elif fmt == 'yaml':
        # pyaml cannot directly dump the weakref to the sql json payload,
        # we also load using dict insertion ordering to preserve the natural
        # ordering of elements in the experiment
        payload = json.loads(
            json.dumps(exp, indent=None),
            object_pairs_hook=OrderedDict)
        payload = yaml.dump(
            payload, indent=2, explicit_start=True, default_flow_style=False,
            Dumper=yamlloader.ordereddict.CSafeDumper)
    else:
        raise abort(400)

    return payload


def download(user_claim: UserClaim, experiment_id: str, org: str,
             workspace: str, fmt: str = 'json',
             filename: str = 'experiment.json',
             mimetype: str = 'application/json'):
    experiment = load_experiment(user_claim, experiment_id, org, workspace)
    url = url_for(
        "workspace_experiment_service.index",org=org, workspace=workspace,
        experiment_id=experiment_id, _external=True)
    payload = prepare_raw(experiment, url=url, fmt=fmt)

    data = io.BytesIO(payload.encode('utf-8'))
    data.seek(0)
    resp = send_file(data, attachment_filename=filename,
                     mimetype=mimetype, as_attachment=True,
                     last_modified=experiment.updated_date)

    # for some unknown reasons, the default behavior returns an empty content
    # if we don't override those two here. I think CherryPy doesn't abide by
    # wsgi.file_wrapper attribute from PEP333
    resp.direct_passthrough = False
    resp.set_data(payload)

    return resp
