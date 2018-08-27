# -*- coding: utf-8 -*-
from functools import wraps
from typing import List, Optional, Tuple, Union

from authlib.flask.oauth2 import current_token
from chaoslib.extension import get_extension
from flask import abort, request, current_app
from chaoshubdashboard.model import db
import shortuuid

from .services import DashboardService, ExperimentService
from .types import Experiment, Extension, UserClaim, Workspace

__all__ = ["load_context"]


def load_context(permissions: Tuple[str, ...] = ('view',)):
    """
    Load org, workspace and experiment from the payload and extension context

    This should be called after load_payload() and load_hub_extension()
    """
    def inner(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_token:
                raise abort(404)

            user_claim = {
                "id": current_token.account_id
            }

            org = kwargs.pop("org", None)
            if not org:
                return abort(404)

            workspace = kwargs.pop("workspace", None)
            if not workspace:
                return abort(404)

            workspace = DashboardService.get_context(
                user_claim, org, workspace)
            if not workspace:
                raise abort(404)

            acls = workspace["context"]["acls"]
            expected_permissions = set(permissions)
            if not set(acls).issuperset(expected_permissions):
                raise abort(404)

            kwargs["org"] = workspace["org"]
            kwargs["workspace"] = workspace
            return f(*args, **kwargs)
        return wrapped
    return inner


def load_experiment(required: bool = True):
    """
    Load the experiment from the request
    """
    def inner(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_token:
                raise abort(404)

            user_claim = {
                "id": current_token.account_id
            }

            experiment_id = kwargs.pop("experiment_id", None)
            if not experiment_id:
                extension = kwargs.get("extension") or {}
                if required and not extension:
                    return abort(404)

                experiment_id = extension.get("experiment")
                if required and not experiment_id:
                    m = "Please, set the `experiment` property in the " \
                        "`chaoshub` extension."
                    r = jsonify({"message": m})
                    r.status_code = 400
                    raise abort(r)

            if experiment_id:
                org = kwargs["org"]
                workspace = kwargs["workspace"]

                experiment = ExperimentService.get_experiment(
                    user_claim, org["id"], workspace["id"], experiment_id)

                if required and not experiment:
                    return abort(404)

                kwargs["experiment"] = experiment
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

    This should be called after load_payload()
    """
    def inner(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            payload = kwargs.get("payload")
            if required and not payload:
                m = "Please, provide an extension block in " \
                    "the payload you sent."
                r = jsonify({"message": m})
                r.status_code = 400
                raise abort(r)

            if payload:
                extension = get_extension(payload, "chaoshub")
                if required and not extension:
                    m = "The Chaos Hub extension entry is missing " \
                        "from the payload. You must provide one for " \
                        "this request."
                    r = jsonify({"message": m})
                    r.status_code = 400
                    raise abort(r)

                kwargs["extension"] = extension
            return f(*args, **kwargs)
        return wrapped
    return inner
