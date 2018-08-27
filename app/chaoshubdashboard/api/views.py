# -*- coding: utf-8 -*-
from datetime import datetime
import os.path
from typing import Any, Dict, Optional
import uuid

from authlib.flask.oauth2 import ResourceProtector, current_token
from authlib.flask.oauth2.signals import token_authenticated
from flask import abort, Blueprint, current_app, jsonify, request, url_for
from flask_accept import accept
import shortuuid

from chaoshubdashboard.model import db

from . import load_experiment, load_hub_extension, load_context, load_payload
from .model import APIAccessToken
from .services import DashboardService, AuthService, ExperimentService
from .types import Org, Workspace, Experiment, Extension

__all__ = ["api"]

api = Blueprint("api", __name__)
require_oauth = ResourceProtector()


def user_authenticated_on_api(sender: ResourceProtector,
                              token: APIAccessToken):
    """
    Set the timestamp of the last successful call made from the given token
    """
    token.last_used_on = datetime.utcnow()
    db.session.commit()

    AuthService.updated_user_access_token(token.to_dict())


token_authenticated.connect(user_authenticated_on_api, require_oauth)


@api.route('', methods=['POST'])
@accept('application/json')
@require_oauth()
@load_payload()
@load_hub_extension(required=False)
@load_context(permissions=('view', 'write'))
@load_experiment(required=False)
def upload_experiment(org: Org, workspace: Workspace, payload: Dict[str, Any],
                      experiment: Experiment = None,
                      extension: Extension = None):
    status = 200
    if not experiment:
        status = 201
        user_claim = {"id": current_token.account_id}
        account_id = current_token.account_id
        experiment = ExperimentService.create_experiment(
            user_claim, org["id"], workspace["id"], payload)

        DashboardService.push_activity({
            "title": experiment["title"],
            "account_id": shortuuid.encode(current_token.account_id),
            "type": "experiment",
            "info": "created",
            "org_id": org["id"],
            "workspace_id": workspace["id"],
            "experiment_id": experiment["id"],
            "visibility": "anonymous"
        })

    x_id = experiment["id"]
    response = jsonify({
        "id": x_id,
        "ref": experiment["ref"]
    })
    response.status_code = status
    response.headers["Location"] = url_for(
        "workspace_experiment_service.index", org=org["name"],
        workspace=workspace["name"], experiment_id=x_id)

    return response


@api.route('<string:experiment_id>/execution', methods=['POST'])
@accept('application/json')
@require_oauth()
@load_payload()
@load_hub_extension(required=False)
@load_context(permissions=('view', 'write'))
@load_experiment()
def upload_run(org: Org, workspace: Workspace, experiment: Experiment,
               payload: Dict[str, Any], extension: Extension = None):
    user_claim = {"id": current_token.account_id}
    execution = ExperimentService.create_execution(
        user_claim, org["id"], workspace["id"], experiment["id"], payload)

    x_id = execution["id"]
    DashboardService.push_activity({
        "title": experiment["title"],
        "account_id": shortuuid.encode(current_token.account_id),
        "type": "execution",
        "info": payload["status"],
        "org_id": org["id"],
        "workspace_id": workspace["id"],
        "experiment_id": experiment["id"],
        "visibility": "collaborator",
        "timestamp": execution["timestamp"]
    })

    response = jsonify({"id": x_id})
    response.status_code = 201
    response.headers["Location"] = url_for(
        "execution_service.index", org=org["name"],
        workspace=workspace["name"],
        experiment_id=experiment["id"],
        timestamp=execution["timestamp"])
    return response
