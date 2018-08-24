# -*- coding: utf-8 -*-
import os.path
from typing import Any, Dict
import uuid

from flask import abort, Blueprint, current_app, redirect, render_template, \
    jsonify, request, session, url_for
import shortuuid
import simplejson as json

from chaoshubdashboard.model import db
from chaoshubdashboard.utils import load_user

from .. import can_write_to_workspace
from ..model import Experiment
from ..services import DashboardService
from ..types import UserClaim

__all__ = ["experiment_service"]

experiment_service = Blueprint("experiment_service", __name__)


@experiment_service.route('/', methods=["GET", "HEAD"])
@load_user(allow_anonymous=True)
def index(user_claim: Dict[str, Any]) -> str:
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    account_id = user_claim["id"]
    result = []
    exps = Experiment.query.filter(Experiment.account_id==account_id).all()
    for exp in exps:
        e = exp.to_public_dict(with_payload=False)
        e["workspace"] = DashboardService.get_experiment_workspace(
            user_claim, e.workspace_id)
        result.append(e)

    return jsonify(result)


@experiment_service.route('new', methods=['GET', 'HEAD'])
@load_user(allow_anonymous=False)
def new(user_claim: UserClaim):
    return render_template('index.html')


@experiment_service.route('new/context', methods=['GET'])
@load_user(allow_anonymous=False)
def context(user_claim: UserClaim):
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    workspaces = DashboardService.get_user_workspaces(user_claim)
    result = []
    for w in workspaces:
        if can_write_to_workspace(w):
            w.pop("context", None)
            result.append(w)

    return jsonify({"workspaces": result})
