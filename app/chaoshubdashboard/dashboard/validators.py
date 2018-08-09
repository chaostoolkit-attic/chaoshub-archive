# -*- coding: utf-8 -*-
from typing import Any, Dict

from flask import abort, jsonify

from .model import Org, Workspace

__all__ = ["validate_org_name", "validate_workspace_name"]


def validate_org_name(org: Dict[str, Any]) -> str:
    """
    Validate the organization's name and raise a failure response if it does
    not meet the expectations, or return the org name otherwise.
    """
    org_name = (org.get("name") or "").strip()
    if not org_name:
        r = jsonify({
            "errors": [{
                "field": "name",
                "message": "A name is required"
            }]
        })
        r.status_code = 400
        raise abort(r)

    if org_name.lower() in ("settings",):
        r = jsonify({
            "errors": [{
                "field": "name",
                "message": "Name is not available"
            }]
        })
        r.status_code = 400
        raise abort(r)

    o = Org.query.filter(Org.name_lower==org_name.lower()).first()
    if o:
        r = jsonify({
            "errors": [{
                "field": "name",
                "message": "Name is not available"
            }]
        })
        r.status_code = 409
        raise abort(r)

    return org_name


def validate_workspace_name(workspace: Dict[str, Any]) -> str:
    """
    Validate the workspace's name and raise a failure response if it does
    not meet the expectations, or return the workspace name otherwise.
    """
    workspace_name = (workspace.get("name") or "").strip()
    if not workspace_name:
        r = jsonify({
            "errors": [{
                "field": "name",
                "message": "A name is required"
            }]
        })
        r.status_code = 400
        raise abort(r)

    reserved = ("settings", "experiment", "gameday", "incident")
    if workspace_name.lower() in reserved:
        r = jsonify({
            "errors": [{
                "field": "name",
                "message": "Name is not available"
            }]
        })
        r.status_code = 400
        raise abort(r)

    w = Workspace.query.filter(
        Workspace.name_lower==workspace_name.lower()).first()
    if w:
        r = jsonify({
            "errors": [{
                "field": "name",
                "message": "Name is not available"
            }]
        })
        r.status_code = 409
        raise abort(r)

    return workspace_name
