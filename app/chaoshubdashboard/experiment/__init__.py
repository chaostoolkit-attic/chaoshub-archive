# -*- coding: utf-8 -*-
from functools import wraps
from typing import List, Optional, Tuple, Union
import uuid

from flask import abort, jsonify, request, current_app
from chaoshubdashboard.model import db
import shortuuid

from .model import Execution as Exec, Experiment as Exp
from .services import DashboardService
from .types import Experiment, Execution, Extension, UserClaim, \
    Run, Workspace

__all__ = ["get_last_updated_experiments", "get_recent_experiments_in_org",
           "get_recent_experiments_in_workspace", "load_org_and_workspace",
           "load_hub_extension", "load_experiment", "load_payload",
           "get_recent_public_experiments_in_workspace", "store_execution",
           "get_recent_executions_in_org", "store_experiment",
           "get_experiment_in_workspace_for_user", "can_write_to_workspace",
           "load_execution"]


def get_experiment(experiment_id: str) -> Optional[Experiment]:
    experiment = Exp.query.filter(Exp.id==experiment_id).first()
    if not experiment:
        return None
    return experiment.to_public_dict(with_payload=False)


def get_experiment_in_workspace_for_user(user_claim: UserClaim, org: str,
                                         workspace: str, experiment_id: str,
                                         include_payload: bool = False) \
                                         -> Optional[Experiment]:
    experiment = Exp.query.filter(
        Exp.account_id==user_claim["id"], Exp.org_id==shortuuid.decode(org),
        Exp.workspace_id==shortuuid.decode(workspace),
        Exp.id==shortuuid.decode(experiment_id)).first()
    if not experiment:
        return None
    return experiment.to_public_dict(with_payload=include_payload)


def store_experiment(user_claim: UserClaim, org: str, workspace: str,
                     payload: Experiment) -> Experiment:
    experiment = Exp(
        shared_ref=uuid.uuid4(),
        account_id=user_claim["id"],
        org_id=shortuuid.decode(org),
        workspace_id=shortuuid.decode(workspace),
        payload=payload
    )
    db.session.add(experiment)
    db.session.commit()

    return experiment.to_public_dict(with_payload=False)


def store_execution(user_claim: UserClaim, org: str, workspace: str,
                    experiment: str, payload: Experiment) -> Experiment:
    execution = Exec(
        experiment_id=shortuuid.decode(experiment),
        account_id=user_claim["id"],
        org_id=shortuuid.decode(org),
        workspace_id=shortuuid.decode(workspace),
        payload=payload,
        status=payload.get('status', 'unknown')
    )
    db.session.add(execution)
    db.session.commit()

    return execution.to_dict()


def get_last_updated_experiments(user_claim: UserClaim) -> List[Experiment]:
    """
    List last updated experiments for the given user.
    """
    account_id = user_claim["id"]

    exps = Exp.query.filter(Exp.account_id==account_id).order_by(
        Exp.updated_date.desc()).limit(5)
    experiments = []
    for e in exps:
        experiments.append(e.to_public_dict(with_payload=False))
    return experiments


def get_recent_experiments_in_workspace(workspace_id: str) -> List[Experiment]:
    """
    List last updated experiments in the given workspace.
    """
    exps = Exp.query.filter(Exp.workspace_id==workspace_id).order_by(
        Exp.updated_date.desc()).limit(5)
    experiments = []
    for e in exps:
        experiments.append(e.to_public_dict(with_payload=False))
    return experiments


def get_recent_experiments_in_org(org_id: str) -> List[Experiment]:
    """
    List last updated experiments in the given organization.
    """
    exps = Exp.query.filter(Exp.org_id==org_id).order_by(
        Exp.updated_date.desc()).limit(5)
    experiments = []
    for e in exps:
        experiments.append(e.to_public_dict(with_payload=False))
    return experiments


def get_recent_public_experiments_in_org(org_id: str,
                                         workspaces: List[str]) \
                                         -> List[Experiment]:
    """
    List last updated public experiments in the given organization's
    workspaces (usually the list of public workspaces in the organization).
    """
    exps = Exp.query.filter(
        Exp.org_id==org_id,
        Exp.workspace_id.in_(workspaces)).order_by(
            Exp.updated_date.desc()).limit(5)
    experiments = []
    for e in exps:
        experiments.append(e.to_public_dict(with_payload=False))
    return experiments


def get_recent_executions_in_org(org_id: str, visibility: str = "status") \
                                 -> List[Run]:
    executions = Exec.query.filter(
        Exec.org_id==org_id).order_by(
            Exec.timestamp.desc()).limit(5)
    runs = []
    for e in executions:
        runs.append(e.to_dict(visibility=visibility))
    return runs


def get_recent_executions_in_workspace(workspace_id: str,
                                       visibility: str = "status") \
                                       -> List[Run]:
    executions = Exec.query.filter(
        Exec.workspace_id==workspace_id).order_by(
            Exec.timestamp.desc()).limit(5)
    runs = []
    for e in executions:
        runs.append(e.to_dict(visibility=visibility))
    return runs


def can_write_to_workspace(workspace: Workspace) -> bool:
    acls = workspace.get("context", {}).get("acls", [])
    return "view" in acls and "write" in acls


def load_org_and_workspace(permissions: Tuple[str, ...] = ('read',)):
    expected_permissions = set(permissions)

    def inner(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            org = kwargs.get("org")
            if not org:
                raise abort(404)

            workspace = kwargs.get("workspace")
            if not workspace:
                raise abort(404)

            org = kwargs.get("org")
            if not org:
                raise abort(404)

            w = DashboardService.get_user_workspace(
                kwargs["user_claim"], org, workspace)
            if not w:
                raise abort(404)

            if set(w["context"]["acls"]).issubset(expected_permissions):
                raise abort(404)

            kwargs["org"] = w["org"]
            kwargs["workspace"] = w

            return f(*args, **kwargs)
        return wrapped
    return inner


def load_experiment():
    """
    Load the experiment from the request
    """
    def inner(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            experiment_id = kwargs.get("experiment_id")
            if experiment_id:
                experiment = Exp.get_by_id(experiment_id)
                if not experiment:
                    m = "Please, provide an experiment."
                    r = jsonify({"message": m})
                    r.status_code = 400
                    raise abort(r)
                kwargs.pop("experiment_id", None)
                kwargs["experiment"] = experiment
            return f(*args, **kwargs)
        return wrapped
    return inner


def load_execution():
    """
    Load the execution from the request
    """
    def inner(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            experiment = kwargs.get("experiment")
            if not experiment:
                raise abort(404)

            timestamp = kwargs.get("timestamp")
            if timestamp is not None:
                execution = experiment.get_execution(timestamp)
                if not execution:
                    m = "Please, provide an execution."
                    r = jsonify({"message": m})
                    r.status_code = 400
                    raise abort(r)
                kwargs.pop("timestamp", None)
                kwargs["execution"] = execution
            return f(*args, **kwargs)
        return wrapped
    return inner


def load_payload():
    """
    Load the payload from the request
    """
    def inner(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if request.method in ["POST", "PATCH", "PUT"]:
                payload = request.json
                if not payload or not isinstance(payload, dict):
                    m = "Please, provide a payload to this request."
                    r = jsonify({"message": m})
                    r.status_code = 400
                    raise abort(r)
                kwargs["payload"] = payload
            return f(*args, **kwargs)
        return wrapped
    return inner


def load_hub_extension(required: bool = False):
    """
    Lookup the Chaos Hub extension in the payload: experiment, gameday...
    """
    def inner(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            payload = request.json
            if required and (not payload or not isinstance(payload, {})):
                m = "Please, provide an extension payload in " \
                    "the payload you sent."
                r = jsonify({"message": m})
                r.status_code = 400
                raise abort(r)

            if payload:
                extensions = payload.get("extensions", [])
                for extension in extensions:
                    if extension.get("name") == "chaoshub":
                        kwargs["extension"] = extension
                        break
                else:
                    if required and "extension" not in kwargs:
                        m = "The Chaos Hub extension entry is missing " \
                            "from the payload. You must provide one for " \
                            "this request."
                        r = jsonify({"message": m})
                        r.status_code = 400
                        raise abort(r)

            return f(*args, **kwargs)
        return wrapped
    return inner
