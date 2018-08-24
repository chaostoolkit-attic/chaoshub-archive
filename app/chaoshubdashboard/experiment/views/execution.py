# -*- coding: utf-8 -*-
from collections import OrderedDict
import copy
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

from .. import load_execution, load_experiment, load_org_and_workspace
from ..model import Execution, Experiment, Schedule
from ..scheduler import is_scheduler_registered, schedule, schedulers
from ..services import AuthService, DashboardService
from ..types import Org, UserClaim, Workspace

__all__ = ["execution_service"]

execution_service = Blueprint("execution_service", __name__)


@execution_service.route('<int:timestamp>', methods=['GET'])
@load_user(allow_anonymous=True)
@load_org_and_workspace(permissions=('read',))
@load_experiment()
@load_execution()
def index(user_claim: UserClaim, org: Org, workspace: Workspace,
          experiment: Experiment, execution: Execution):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')


@execution_service.route('', methods=['GET'])
@load_user(allow_anonymous=True)
@load_org_and_workspace(permissions=('read',))
@load_experiment()
def executions(user_claim: UserClaim, org: Org, workspace: Workspace,
               experiment: Experiment):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    executions = Execution.query.filter(
        Execution.experiment_id==experiment.id).order_by(
            Execution.timestamp.desc()).all()

    visibilities = workspace["settings"]["visibility"]["execution"]
    if not user_claim:
        visibility = visibilities["anonymous"]
    else:
        visibility = visibilities["members"]

    result = []
    for execution in executions:
        result.append(execution.to_dict(visibility))

    return jsonify(result)


@execution_service.route('<int:timestamp>/context', methods=['GET'])
@accept("application/json")
@load_user(allow_anonymous=True)
@load_org_and_workspace(permissions=('read',))
@load_experiment()
@load_execution()
def context(user_claim: UserClaim, org: Org, workspace: Workspace,
          experiment: Experiment, execution: Execution):
    visibilities = workspace["settings"]["visibility"]["execution"]
    if not user_claim:
        visibility = visibilities["anonymous"]
    else:
        visibility = visibilities["members"]

    return jsonify(execution.to_dict(visibility))
