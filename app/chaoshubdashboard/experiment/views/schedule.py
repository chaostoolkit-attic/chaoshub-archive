# -*- coding: utf-8 -*-
from collections import OrderedDict
import io
import os.path
from typing import Any, Dict
import uuid

import dateparser
from flask import abort, Blueprint, current_app, redirect, render_template, \
    jsonify, request, send_file, session, url_for
from flask_accept import accept, accept_fallback
import shortuuid
import simplejson as json
import yaml
import yamlloader

from chaoshubdashboard.model import db
from chaoshubdashboard.utils import cache, load_user

from .. import load_experiment, load_org_and_workspace
from ..model import Experiment, Schedule
from ..scheduler import is_scheduler_registered, schedule, schedulers
from ..services import AuthService, DashboardService
from ..types import Org, UserClaim, Workspace

__all__ = ["schedule_experiment_service"]

schedule_experiment_service = Blueprint(
    "schedule_experiment_service", __name__)


@schedule_experiment_service.route('', methods=['GET'])
@load_user(allow_anonymous=False)
@load_org_and_workspace(permissions=('read', 'write'))
@load_experiment()
def index(user_claim: UserClaim, org: Org, workspace: Workspace,
          experiment: Experiment):
    return render_template('index.html')


@schedule_experiment_service.route('with/context', methods=["GET"])
@load_user(allow_anonymous=False)
@load_org_and_workspace(permissions=('read', 'write'))
@load_experiment()
def context(user_claim: UserClaim, org: Org, workspace: Workspace,
            experiment: Experiment):
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    context: Dict[str, Any] = {
        "tokens": [],
        "schedulers": []
    }

    account_id = user_claim["id"]
    tokens = AuthService.get_user_access_tokens(user_claim)
    for token in tokens:
        context["tokens"].append({
            "id": token["id"],
            "name": token["name"]
        })

    registered_schedulers = schedulers()
    for s in sorted(registered_schedulers.keys()):
        sched = registered_schedulers[s]
        context["schedulers"].append({
            "name": s,
            "description": sched.description,
            "version": sched.version
        })

    context["schedules"] = []
    schedules = Schedule.query.filter(
        Schedule.account_id==account_id,
        Schedule.experiment_id==experiment.id).all()
    for schedule in schedules:
        context["schedules"].append(schedule.to_dict())

    return jsonify(context)


@schedule_experiment_service.route('', methods=['POST'])
@load_user(allow_anonymous=False)
@load_org_and_workspace(permissions=('read', 'write'))
@load_experiment()
def schedule_execution(user_claim: UserClaim, org: Org, workspace: Workspace,
                       experiment: Experiment):
    definition = request.json
    if not definition:
        return abort(400)

    account_id = user_claim["id"]

    scheduler = definition.get("scheduler")
    if not is_scheduler_registered(scheduler):
        r = jsonify({
            "errors": [{
                "field": "scheduler",
                "message": "Invalid scheduler"
            }]
        })
        r.status_code = 400
        return abort(r)

    token_id = shortuuid.decode(definition.get("token"))
    token = AuthService.get_user_access_token(user_claim, token_id)
    if not token:
        r = jsonify({
            "errors": [{
                "field": "token",
                "message": "Invalid token"
            }]
        })
        r.status_code = 400
        return abort(r)

    date = definition.get("date")
    if not date:
        r = jsonify({
            "errors": [{
                "field": "date",
                "message": "Specify a date"
            }]
        })
        r.status_code = 400
        return abort(r)

    time = definition.get("time")
    if not time:
        r = jsonify({
            "errors": [{
                "field": "date",
                "message": "Specify a time"
            }]
        })
        r.status_code = 400
        return abort(r)

    scheduled_date = dateparser.parse("{}T{}".format(date, time))

    account_id = user_claim["id"]
    s = Schedule(
        account_id=account_id,
        org_id=shortuuid.decode(org["id"]),
        workspace_id=shortuuid.decode(workspace["id"]),
        experiment_id=experiment.id,
        token_id=shortuuid.decode(token["id"]),
        definition=definition,
        scheduled=scheduled_date
    )
    db.session.add(s)
    db.session.commit()

    context = s.to_dict()
    context["hub_url"] = url_for(
        "dashboard_service.index", _external=True).rstrip('/')
    context["token"] = token["access_token"]
    context["org"] = org
    context["workspace"] = workspace
    payload = json.loads(json.dumps(experiment.payload))
    context["experiment"] = {
        "id": shortuuid.encode(experiment.id),
        "payload": payload
    }
    set_chaoshub_extension_to_experiment(experiment, payload)
    s.info = schedule(scheduler, context)
    db.session.commit()

    DashboardService.push_activity({
        "title": "Schedule",
        "account_id": user_claim["short_id"],
        "org_id": org["id"],
        "workspace_id": workspace["id"],
        "type": "schedule",
        "info": "created",
        "visibility": "collaborator"
    })

    return jsonify(s.to_dict()), 201


def set_chaoshub_extension_to_experiment(experiment: Experiment,
                                         definition: Dict[str, Any]):
    if "extensions" not in definition:
        definition["extensions"] = []

    for ext in definition["extensions"]:
        ext_name = ext.get("name")
        if ext_name == "chaoshub":
            ext["experiment"] = shortuuid.encode(experiment.id)
            ext["workspace"] = shortuuid.encode(experiment.workspace_id)
            ext["org"] = shortuuid.encode(experiment.org_id)
            break
    else:
        definition["extensions"].append({
            "name": "chaoshub",
            "experiment": shortuuid.encode(experiment.id),
            "workspace": shortuuid.encode(experiment.workspace_id),
            "org": shortuuid.encode(experiment.org_id)
        })
