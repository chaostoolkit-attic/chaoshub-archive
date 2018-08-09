# -*- coding: utf-8 -*-
from collections import OrderedDict
import io
import os.path
from typing import Any, Dict
import uuid

from flask import abort, Blueprint, current_app, redirect, render_template, \
    jsonify, request, send_file, session, url_for
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
    '<string:experiment_id>/run/<string:run_id>', methods=['GET'])
@accept_fallback
@load_user(allow_anonymous=True)
def run_index(user_claim: UserClaim, experiment_id: str, org: str,
              workspace: str, run_id: str):
    return render_template('index.html')


@workspace_experiment_service.route(
    '<string:experiment_id>/schedule', methods=['GET'])
@load_user(allow_anonymous=False)
def schedule(user_claim: UserClaim, experiment_id: str, org: str,
             workspace: str):
    return render_template('index.html')


@workspace_experiment_service.route('<string:experiment_id>', methods=['GET'])
@index.support("application/json")
@load_user(allow_anonymous=True)
def context(user_claim: UserClaim, experiment_id: str, org: str, workspace: str):
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


def download(user_claim: UserClaim, experiment_id: str, org: str,
             workspace: str, fmt: str = 'json',
             filename: str = 'experiment.json',
             mimetype: str = 'application/json'):

    experiment_id = shortuuid.decode(experiment_id)
    experiment = Experiment.query.filter(Experiment.id==experiment_id).first()
    if not experiment:
        return abort(404)

    w = DashboardService.get_workspace(user_claim, org, workspace)
    if not w:
        return abort(404)

    if "view" not in w["context"]["acls"]:
        return abort(404)

    if fmt == 'json':
        payload = json.dumps(experiment.payload, indent=2)
    elif fmt == 'yaml':
        # pyaml cannot directly dump the weakref to the sql json payload,
        # we also load using dict insertion ordering to preserve the natural
        # ordering of elements in the experiment
        payload = json.loads(
            json.dumps(experiment.payload, indent=None),
            object_pairs_hook=OrderedDict)
        payload = yaml.dump(
            payload, indent=2, explicit_start=True, default_flow_style=False,
            Dumper=yamlloader.ordereddict.CSafeDumper)
    else:
        return abort(400)

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
