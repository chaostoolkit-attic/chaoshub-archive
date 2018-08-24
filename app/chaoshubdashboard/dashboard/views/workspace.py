# -*- coding: utf-8 -*-
import os
from typing import Any, Dict, List

from flask import abort, Blueprint, current_app, jsonify, redirect, \
    render_template, request, session, url_for
import shortuuid

from chaoshubdashboard.utils import load_user

from .. import get_workspace_from_url, \
    is_org_viewable, is_workspace_viewable, load_org_and_workspace, \
    lookup_collaborators, record_activity, get_caller_workspace_activities

from ..model import db, OrgsMembers, WorkpacesMembers, Org, OrgType, \
    UserAccount, Workspace, WorkspaceType, ActivityVisibility
from ..services import ExperimentService
from ..types import UserClaim
from ..validators import validate_workspace_name


__all__ = ["get_workspace", "get_workspaces",
           "is_workspace_visible_to_user", "workspace_service"]

workspace_service = Blueprint("workspace_service", __name__)


@workspace_service.route('', methods=["GET", "HEAD"])
@load_user(allow_anonymous=True)
@load_org_and_workspace(
    redirect_to="workspace_service.index", allow_anonymous=True)
def index(user_claim: Dict[str, Any], org: Org, workspace: Workspace) -> str:
    return render_template('index.html')


@workspace_service.route('dashboard', methods=["GET", "HEAD"])
@load_user(allow_anonymous=True)
@load_org_and_workspace(
    redirect_to="workspace_service.dashboard", allow_anonymous=True)
def dashboard(user_claim: Dict[str, Any], org: Org,
              workspace: Workspace) -> str:
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    org_owner = False
    workspace_owner = False
    info = {}

    caller = None
    if user_claim:
        account_id = user_claim["id"]
        account = UserAccount.query.filter(UserAccount.id==account_id).first()
        caller = account.to_short_dict()
        caller["org_member"] = org.is_member(account_id)
        caller["org_owner"] = org_owner = org.is_owner(account_id)
        caller["workspace_owner"] = workspace.is_owner(account_id)
        caller["workspace_collaborator"] = \
            workspace.is_collaborator(account_id)
        info["requested_by"] = caller

    exps = ExperimentService.get_workspace_last_experiments(workspace.id)
    info["activities"] = get_caller_workspace_activities(  # type: ignore
        workspace, caller)
    info["experiments"] = exps
    info["org"] = org.to_short_dict()
    info["workspace"] = workspace.to_dict()
    w_members = WorkpacesMembers.query.filter(
        WorkpacesMembers.workspace_id==workspace.id).limit(5)
    info["collaborators"] = [m.account.to_short_dict() for m in w_members]

    return jsonify(info)


@workspace_service.route('lookup/collaborator', methods=["GET", "HEAD"])
@load_user(allow_anonymous=True)
@load_org_and_workspace(
    redirect_to="workspace_service.find_collaborator", allow_anonymous=True)
def find_collaborator(user_claim: UserClaim, org: Org, workspace: Workspace):
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    return jsonify(lookup_collaborators(workspace, request.args.get("q")))


@workspace_service.route('settings', methods=["GET", "HEAD"])
@load_user(allow_anonymous=False)
@load_org_and_workspace(
    redirect_to="workspace_service.settings", allow_anonymous=False)
def settings(user_claim: UserClaim, org: Org, workspace: Workspace):
    return render_template('index.html')


@workspace_service.route('settings/general', methods=["GET", "HEAD"])
@load_user(allow_anonymous=False)
@load_org_and_workspace(
    redirect_to="workspace_service.general", allow_anonymous=False)
def general(user_claim: UserClaim, org: Org, workspace: Workspace):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    account_id = user_claim["id"]
    account = UserAccount.query.filter(UserAccount.id==account_id).first()

    if not org.is_member(account_id):
        return abort(404)

    caller = account.to_short_dict()
    caller["org_owner"] = org.is_owner(account_id)
    caller["workspace_owner"] = workspace.is_owner(account_id)

    result = {
        "requested_by": caller,
        "org": org.to_dict(),
        "workspace": workspace.to_dict()
    }

    return jsonify(result)


@workspace_service.route('settings/collaborators', methods=["GET", "HEAD"])
@load_user(allow_anonymous=False)
@load_org_and_workspace(
    redirect_to="workspace_service.collaborators", allow_anonymous=False)
def collaborators(user_claim: Dict[str, Any], org: Org,
                  workspace: Workspace) -> str:
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    account_id = user_claim["id"]
    account = UserAccount.query.filter(UserAccount.id==account_id).first()

    if not workspace.is_collaborator(account_id) or \
       not org.is_member(account_id):
        return abort(404)

    w_collaborators = WorkpacesMembers.query.filter(
        WorkpacesMembers.workspace_id==workspace.id).paginate(
            max_per_page=10, error_out=False)

    users: List[Dict[str, Any]] = []
    for m in w_collaborators.items:
        d = m.account.to_short_dict()
        d["workspace_owner"] = m.is_owner
        users.append(d)

    caller = account.to_short_dict()
    caller["org_owner"] = org.is_owner(account_id)
    caller["workspace_owner"] = workspace.is_owner(account_id)

    result = {
        "collaborators": users,
        "requested_by": caller,
        "org": org.to_short_dict(),
        "workspace": workspace.to_short_dict(),
        "paging": {
            "total": w_collaborators.total,
            "prev": None,
            "next": None
        }
    }

    if w_collaborators.has_prev:
        result["paging"]["prev"] = w_collaborators.prev_num

    if w_collaborators.has_next:
        result["paging"]["next"] = w_collaborators.next_num

    return jsonify(result)


@workspace_service.route('settings/general/name', methods=["PATCH"])
@load_user(allow_anonymous=False)
@load_org_and_workspace(
    redirect_to="workspace_service.new_name", allow_anonymous=False)
def new_name(user_claim: UserClaim, org: Org, workspace: Workspace):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    account_id = user_claim["id"]
    account = UserAccount.query.filter(UserAccount.id==account_id).first()

    if not workspace.is_owner(account_id):
        return abort(404)

    new_workspace_name = request.json
    workspace_name = validate_workspace_name(new_workspace_name)
    workspace.name = workspace_name
    workspace.name_lower = workspace_name.lower()
    db.session.commit()

    record_activity({
        "title": workspace.name,
        "account_id": shortuuid.encode(account.id),
        "type": "workspace",
        "info": "updated",
        "org_id": shortuuid.encode(org.id),
        "workspace_id": shortuuid.encode(workspace.id),
        "visibility": ActivityVisibility.owner
    })

    return "", 204


@workspace_service.route('settings/collaborators', methods=["POST"])
@load_user(allow_anonymous=False)
@load_org_and_workspace(
    redirect_to="workspace_service.add_user_as_collaborator",
    allow_anonymous=False)
def add_user_as_collaborator(user_claim: Dict[str, Any], org: Org,
                             workspace: Workspace):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    # the user making the request
    account_id = user_claim["id"]
    if not workspace.is_owner(account_id):
        return abort(400)

    user = request.json
    if not user:
        return abort(400)

    user_id = user.get("id")
    if not user_id:
        return abort(400)

    # the user to add
    account = UserAccount.query.filter(
        UserAccount.id==shortuuid.decode(user_id)).first()
    if not account:
        return abort(400)

    if workspace.is_collaborator(account.id):
        return "", 204

    membership = workspace.add_collaborator(account.id)
    db.session.commit()

    record_activity({
        "title": workspace.name,
        "account_id": shortuuid.encode(account.id),
        "type": "workspace",
        "info": "collaborator added",
        "org_id": shortuuid.encode(org.id),
        "workspace_id": shortuuid.encode(workspace.id),
        "visibility": ActivityVisibility.authenticated
    })

    return jsonify(account.to_short_dict()), 201


@workspace_service.route(
    'settings/collaborators/<string:user_id>', methods=["DELETE"])
@load_user(allow_anonymous=False)
@load_org_and_workspace(
    redirect_to="org_service.general", allow_anonymous=False)
def remove_collaborator_from_workspace(user_claim: Dict[str, Any], org: Org,
                                       workspace: Workspace, user_id: str):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    # the user making the request
    account_id = user_claim["id"]
    if not workspace.is_owner(account_id):
        return abort(400)

    # the user to remove
    account = UserAccount.query.filter(
        UserAccount.id==shortuuid.decode(user_id)).first()
    if not account:
        return "", 204

    if workspace.is_owner(account.id) and workspace.has_single_owner():
        return abort(400)

    workspace.remove_collaborator(user_id)
    db.session.commit()

    record_activity({
        "title": workspace.name,
        "account_id": shortuuid.encode(account.id),
        "type": "workspace",
        "info": "collaborator deleted",
        "org_id": shortuuid.encode(org.id),
        "workspace_id": shortuuid.encode(workspace.id),
        "visibility": ActivityVisibility.authenticated
    })

    return "", 204


@workspace_service.route(
    'settings/members/<string:user_id>', methods=["PATCH"])
@load_user(allow_anonymous=False)
@load_org_and_workspace(
    redirect_to="org_service.general", allow_anonymous=False)
def patch_membership(user_claim: Dict[str, Any], org: Org,
                     workspace: Workspace, user_id: str):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    # the user making the request
    account_id = user_claim["id"]
    if not workspace.is_owner(account_id):
        return abort(400)

    # the user to amend
    user = request.json
    if not user:
        return abort(400)

    user_id = user.get("id")
    if not user_id:
        return abort(400)

    account = UserAccount.query.filter(
        UserAccount.id==shortuuid.decode(user_id)).first()
    if not account:
        return "", 204

    turn_owner = user.get("workspace_owner", False)
    if turn_owner and workspace.is_collaborator(account.id):
        workspace.make_owner(account.id)
    elif not turn_owner and workspace.is_owner(account.id):
        if workspace.has_single_owner():
            return abort(400)
        workspace.make_collaborator(account.id)

    db.session.commit()

    record_activity({
        "title": workspace.name,
        "account_id": shortuuid.encode(account.id),
        "type": "workspace",
        "info": "collaborator updated",
        "org_id": shortuuid.encode(org.id),
        "workspace_id": shortuuid.encode(workspace.id),
        "visibility": ActivityVisibility.authenticated
    })

    return "", 200
