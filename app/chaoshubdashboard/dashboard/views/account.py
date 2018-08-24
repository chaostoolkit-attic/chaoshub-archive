# -*- coding: utf-8 -*-
import os.path
from typing import Any, Dict

from flask import abort, Blueprint, current_app, jsonify, redirect, \
    render_template, Response, request, session, url_for
import shortuuid
from sqlalchemy import distinct, or_

from chaoshubdashboard.model import db
from chaoshubdashboard.utils import load_user

from .. import record_activity
from ..model import OrgsMembers, WorkpacesMembers, Org, OrgType, \
    UserAccount, UserInfo, Workspace, WorkspaceType, ExperimentVisibility, \
    ExecutionVisibility, DEFAULT_ORG_SETTINGS, DEFAULT_WORKSPACE_SETTINGS, \
    ActivityVisibility, Activity
from ..services import AuthService
from ..types import UserClaim
from ..validators import validate_org_name


__all__ = ["account_service"]

account_service = Blueprint("account_service", __name__)


@account_service.route('/')
@load_user(allow_anonymous=True)
def account(user_claim: UserClaim):
    return render_template('index.html')


@account_service.route('profile', methods=["GET"])
@load_user(allow_anonymous=False)
def profile(user_claim: UserClaim):
    if request.headers.get('Accept') == 'application/json':
        info = UserInfo.get_for_account(user_claim['id'])
        return jsonify(info.to_dict())
    return render_template('index.html')


@account_service.route('profile', methods=["POST"])
@load_user(allow_anonymous=False)
def update_profile(user_claim: UserClaim):
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    profile = request.json
    account_id = user_claim['id']
    info = UserInfo.get_for_account(account_id)

    email = profile.get("email")
    if email is not None:
        email = email.lower().strip()
        if email:
            other = UserInfo.query.filter(
                UserInfo.email==email, UserInfo.account_id!=account_id).first()
            if other:
                resp = jsonify({"message": "Email already used."})
                resp.status_code = 400
                return resp
        info.email = email

    info.username = profile.get("username")
    info.name = profile.get("name")
    info.bio = profile.get("bio")
    info.company = profile.get("company")

    db.session.commit()

    record_activity({
        "title": "Profile",
        "account_id": user_claim["short_id"],
        "type": "profile",
        "info": "updated",
        "visibility": ActivityVisibility.owner
    })

    return "", 204


@account_service.route('tokens', methods=["GET"])
@load_user(allow_anonymous=False)
def tokens(user_claim: UserClaim):
    if request.headers.get('Accept') == 'application/json':
        tokens = user_claim.get("tokens", [])
        return jsonify([token for token in tokens if not token["revoked"]])
    return render_template('index.html')


@account_service.route('tokens', methods=["POST"])
@load_user(allow_anonymous=False)
def new_token(user_claim: UserClaim):
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    token = request.json

    token_name = token.get("name")
    if not token_name:
        return abort("404")

    access_token = AuthService.new_access_token(user_claim, token_name)

    record_activity({
        "title": "Access Token",
        "account_id": user_claim["short_id"],
        "type": "token",
        "info": "created",
        "visibility": ActivityVisibility.owner
    })

    return jsonify({
        "id": access_token["id"],
        "name": access_token["name"],
        "issued_at": access_token["issued_at"],
        "last_used": access_token["last_used"],
        "access_token": access_token["access_token"]
    }), 201


@account_service.route('tokens/<token_id>', methods=["DELETE"])
@load_user(allow_anonymous=False)
def revoke_token(token_id: str, user_claim: UserClaim):
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    token_id = shortuuid.decode(token_id)
    AuthService.revoke_user_access_token(user_claim, token_id)

    record_activity({
        "title": "Access Token",
        "account_id": user_claim["short_id"],
        "type": "token",
        "info": "revoked",
        "visibility": ActivityVisibility.owner
    })

    return jsonify(None), 204


@account_service.route('orgs', methods=["GET"])
@load_user(allow_anonymous=False)
def orgs(user_claim: UserClaim):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    account_id = user_claim["id"]
    assocs = OrgsMembers.query.filter(
        OrgsMembers.account_id==account_id).paginate(
            max_per_page=5, error_out=False)

    orgs = []
    for assoc in assocs.items:
        o = assoc.organization.to_dict()
        o["owner"] = assoc.is_owner
        orgs.append(o)

    result = {
        "orgs": orgs,
        "paging": {
            "total": assocs.total,
            "prev": None,
            "next": None
        }
    }

    if assocs.has_prev:
        result["paging"]["prev"] = assocs.prev_num  # type: ignore

    if assocs.has_next:
        result["paging"]["next"] = assocs.next_num  # type: ignore

    return jsonify(result)


@account_service.route('orgs', methods=["POST"])
@load_user(allow_anonymous=False)
def new_org(user_claim: UserClaim):
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    org = request.json
    org_name = validate_org_name(org)

    org_settings = DEFAULT_ORG_SETTINGS.copy()
    settings = org.get("settings")
    for k in ("url", "email", "description"):
        org_settings["meta"][k] = settings.get(k)  # type: ignore

    account = UserAccount.query.filter(
        UserAccount.id==user_claim["id"]).first()
    o = Org(
        name=org_name, name_lower=org_name.lower(), kind=OrgType.collaborative,
        settings=org_settings)
    assoc = OrgsMembers(account=account, organization=o, is_owner=True)

    db.session.add(o)
    db.session.add(assoc)
    db.session.commit()

    record_activity({
        "title": o.name,
        "account_id": user_claim["short_id"],
        "type": "organization",
        "info": "created",
        "org_id": shortuuid.encode(o.id),
        "visibility": ActivityVisibility.owner
    })

    result = o.to_dict()
    result["owner"] = True
    return jsonify(result), 201


@account_service.route('workspaces', methods=["GET"])
@load_user(allow_anonymous=False)
def workspaces(user_claim: UserClaim):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    account_id = user_claim["id"]
    orgs_memberships = OrgsMembers.query.filter(
        OrgsMembers.account_id==account_id).all()

    workspaces = Workspace.query.distinct(Workspace.id).filter(
        or_(
            Workspace.id.in_(
                db.session.query(Workspace.id).filter(
                    Workspace.org_id.in_(
                        db.session.query(OrgsMembers.org_id).filter(
                            OrgsMembers.account_id==account_id)))),
            Workspace.id.in_(
                db.session.query(WorkpacesMembers.workspace_id).filter(
                    WorkpacesMembers.account_id==account_id)))
    ).paginate(max_per_page=5, error_out=False)

    orgs = []
    for membership in orgs_memberships:
        o = membership.organization.to_dict()
        o["owner"] = membership.is_owner
        orgs.append(o)

    ws = []
    for workspace in workspaces.items:
        w = workspace.to_dict()
        w["owner"] = workspace.is_owner(account_id)
        ws.append(w)

    result = {
        "orgs": orgs,
        "workspaces": ws,
        "paging": {
            "total": workspaces.total,
            "prev": None,
            "next": None
        }
    }

    if workspaces.has_prev:
        result["paging"]["prev"] = workspaces.prev_num  # type: ignore

    if workspaces.has_next:
        result["paging"]["next"] = workspaces.next_num  # type: ignore

    return jsonify(result)


@account_service.route('workspaces', methods=["POST"])
@load_user(allow_anonymous=False)
def new_workspace(user_claim: UserClaim):
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    workspace = request.json
    if not workspace:
        return abort(400)

    workspace_name = workspace.get("name", "").strip()
    if not workspace_name:
        r = jsonify({
            "errors": [{
                "field": "name",
                "message": "A name is required"
            }]
        })
        r.status_code = 400
        return abort(r)

    org_id = (workspace.get("org") or "").strip()
    if not org_id:
        r = jsonify({
            "errors": [{
                "field": "org",
                "message": "Organization must be set"
            }]
        })
        r.status_code = 400
        return abort(r)

    org = Org.query.filter(Org.id==shortuuid.decode(org_id)).first()
    if not org:
        r = jsonify({
            "errors": [{
                "field": "org",
                "message": "Organization does not exist"
            }]
        })
        r.status_code = 400
        return abort(r)

    other = Workspace.query.filter(
        Workspace.org_id==org.id, Workspace.name==workspace_name).first()
    if other:
        r = jsonify({
            "errors": [{
                "field": "name",
                "message": "Name is already used in this organization"
            }]
        })
        r.status_code = 409
        return abort(r)

    experiment_visibility = ExperimentVisibility.private
    try:
        experiment_visibility = ExperimentVisibility(
            workspace.get("visibility", {}).get(
                "experiment", experiment_visibility)).value
    except ValueError:
        r = jsonify({
            "errors": [{
                "field": "visibility",
                "message": "Experiment visibility is not recognized"
            }]
        })
        r.status_code = 400
        return abort(r)

    execution_visibility = ExecutionVisibility.none
    try:
        execution_visibility = ExecutionVisibility(
            workspace.get("visibility", {}).get(
                "execution", execution_visibility)).value
    except ValueError:
        r = jsonify({
            "errors": [{
                "field": "visibility",
                "message": "Execution visibility is not recognized"
            }]
        })
        r.status_code = 400
        return abort(r)

    settings = DEFAULT_WORKSPACE_SETTINGS.copy()
    settings["visibility"]["execution"]["anonymous"] = execution_visibility
    settings["visibility"]["experiment"]["anonymous"] = experiment_visibility
    account = UserAccount.query.filter(
        UserAccount.id==user_claim["id"]).first()
    w = Workspace(
        name=workspace_name, name_lower=workspace_name.lower(),
        settings=settings, org_id=org.id,
        kind=WorkspaceType.public)
    assoc = WorkpacesMembers(account=account, workspace=w, is_owner=True)

    db.session.add(w)
    db.session.add(assoc)
    db.session.commit()

    record_activity({
        "title": w.name,
        "account_id": user_claim["short_id"],
        "type": "workspace",
        "info": "created",
        "org_id": shortuuid.encode(org.id),
        "workspace_id": shortuuid.encode(w.id),
        "visibility": ActivityVisibility.owner
    })

    result = w.to_dict()
    result["owner"] = True
    return jsonify(result), 201
