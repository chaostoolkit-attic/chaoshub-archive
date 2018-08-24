# -*- coding: utf-8 -*-
import os
from typing import Any, Dict, List
from urllib.parse import urlparse

from flask import abort, Blueprint, current_app, jsonify, redirect, \
    render_template, request, session, url_for
import shortuuid

from chaoshubdashboard.model import db
from chaoshubdashboard.utils import load_user

from .. import can_org_be_deleted, get_org_from_url, \
    is_org_viewable, load_org, lookup_members, lookup_workspaces, \
    record_activity, get_caller_org_activities
from ..model import Activity, ActivityVisibility, Org, OrgsMembers, OrgType, \
    UserAccount
from ..services import ExperimentService
from ..types import UserClaim
from ..validators import validate_org_name

__all__ = ["org_service"]

org_service = Blueprint("org_service", __name__)


@org_service.route('', methods=["GET", "HEAD"])
@load_user(allow_anonymous=True)
@load_org(redirect_to="org_service.index", allow_anonymous=True)
def index(user_claim: Dict[str, Any], org: Org) -> str:
    return render_template('index.html')


@org_service.route('', methods=["DELETE"])
@load_user(allow_anonymous=False)
@load_org(redirect_to="org_service.index", allow_anonymous=False)
def deletion(user_claim: Dict[str, Any], org: Org):
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    account_id = user_claim["id"]
    if not can_org_be_deleted(account_id, org):
        return abort(403)

    db.session.delete(org)
    db.session.commit()

    record_activity({
        "title": org.name,
        "account_id": account_id,
        "kind": "organization",
        "info": "deleted",
        "org_id": org.id,
        "visibility": ActivityVisibility.owner
    })

    return "", 204


@org_service.route('dashboard', methods=["GET", "HEAD"])
@load_user(allow_anonymous=True)
@load_org(redirect_to="org_service.dashboard", allow_anonymous=True)
def dashboard(user_claim: Dict[str, Any], org: Org) -> str:
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    org_owner = False
    info = {}

    caller = None
    if user_claim:
        account_id = user_claim["id"]
        account = UserAccount.query.filter(UserAccount.id==account_id).first()
        caller = account.to_short_dict()
        caller["org_member"] = org.is_member(account_id)
        caller["org_owner"] = org_owner = org.is_owner(account_id)
        info["requested_by"] = caller

    info["activities"] = get_caller_org_activities(org, caller)  # type: ignore
    o_members = OrgsMembers.query.filter(
        OrgsMembers.org_id==org.id).limit(5)
    info["members"] = [m.account.to_short_dict() for m in o_members]

    if org_owner:
        info["org"] = org.to_dict()
    else:
        info["org"] = org.to_dict(public_workspaces_only=True)

    return jsonify(info)


@org_service.route('lookup/member', methods=["GET", "HEAD"])
@load_user(allow_anonymous=True)
@load_org(redirect_to="org_service.find_member", allow_anonymous=True)
def find_member(user_claim: UserClaim, org: Org):
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    return jsonify(lookup_members(org, request.args.get("q")))


@org_service.route('lookup/workspace', methods=["GET", "HEAD"])
@load_user(allow_anonymous=True)
@load_org(redirect_to="org_service.find_workspace", allow_anonymous=True)
def find_workspace(user_claim: UserClaim, org: Org):
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    account_id = user_claim["id"] if user_claim else None
    return jsonify(
        lookup_workspaces(org, request.args.get("q"), account_id))


@org_service.route('settings', methods=["GET", "HEAD"])
@load_user(allow_anonymous=False)
@load_org(redirect_to="org_service.settings", allow_anonymous=False)
def settings(user_claim: UserClaim, org: Org):
    return render_template('index.html')


@org_service.route('settings/general', methods=["GET", "HEAD"])
@load_user(allow_anonymous=False)
@load_org(redirect_to="org_service.general", allow_anonymous=False)
def general(user_claim: UserClaim, org: Org):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    account_id = user_claim["id"]
    account = UserAccount.query.filter(UserAccount.id==account_id).first()

    if not org.is_member(account_id):
        return abort(404)

    caller = account.to_short_dict()
    caller["org_owner"] = org.is_owner(account_id)

    result = {
        "requested_by": caller,
        "org": org.to_dict()
    }

    return jsonify(result)


@org_service.route('settings/general/name', methods=["PATCH"])
@load_user(allow_anonymous=False)
@load_org(redirect_to="org_service.general", allow_anonymous=False)
def new_name(user_claim: UserClaim, org: Org):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    account_id = user_claim["id"]
    account = UserAccount.query.filter(UserAccount.id==account_id).first()

    if not org.is_owner(account_id):
        return abort(404)

    new_org_name = request.json
    org_name = validate_org_name(new_org_name)
    org.name = org_name
    org.name_lower = org_name.lower()
    db.session.commit()

    record_activity({
        "title": org.name,
        "account_id": account_id,
        "kind": "organization",
        "info": "updated",
        "org_id": org.id,
        "visibility": ActivityVisibility.authenticated
    })

    return "", 204


@org_service.route('settings/general/details', methods=["PATCH"])
@load_user(allow_anonymous=False)
@load_org(redirect_to="org_service.general", allow_anonymous=False)
def new_details(user_claim: UserClaim, org: Org):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    account_id = user_claim["id"]
    account = UserAccount.query.filter(UserAccount.id==account_id).first()

    if not org.is_owner(account_id):
        return abort(404)

    new_details = request.json
    org.settings = new_details
    db.session.commit()

    record_activity({
        "title": org.name,
        "account_id": account_id,
        "kind": "organization",
        "info": "updated",
        "org_id": org.id,
        "visibility": ActivityVisibility.authenticated
    })

    return "", 204


@org_service.route('settings/members', methods=["GET", "HEAD"])
@load_user(allow_anonymous=False)
@load_org(redirect_to="org_service.members", allow_anonymous=False)
def members(user_claim: Dict[str, Any], org: Org) -> str:
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    account_id = user_claim["id"]
    account = UserAccount.query.filter(UserAccount.id==account_id).first()

    if not org.is_member(account_id):
        return abort(404)

    o_members = OrgsMembers.query.filter(
        OrgsMembers.org_id==org.id).paginate(
            max_per_page=10, error_out=False)

    users: List[Dict[str, Any]] = []
    for m in o_members.items:
        d = m.account.to_short_dict()
        d["org_owner"] = m.is_owner
        users.append(d)

    caller = account.to_short_dict()
    caller["org_owner"] = org.is_owner(account_id)

    result = {
        "users": users,
        "requested_by": caller,
        "org": org.to_short_dict(),
        "paging": {
            "total": o_members.total,
            "prev": None,
            "next": None
        }
    }

    if o_members.has_prev:
        result["paging"]["prev"] = o_members.prev_num

    if o_members.has_next:
        result["paging"]["next"] = o_members.next_num

    return jsonify(result)


@org_service.route('settings/members', methods=["POST"])
@load_user(allow_anonymous=False)
@load_org(
    redirect_to="org_service.add_user_as_org_member", allow_anonymous=False)
def add_user_as_org_member(user_claim: Dict[str, Any], org: Org):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    # the user making the request
    account_id = user_claim["id"]
    if not org.is_owner(account_id):
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

    if org.is_member(account.id):
        return "", 204

    membership = org.add_member(account.id)
    db.session.commit()

    record_activity({
        "title": org.name,
        "account_id": account_id,
        "kind": "organization",
        "info": "collaborator added",
        "org_id": org.id,
        "visibility": ActivityVisibility.authenticated
    })

    return jsonify(account.to_short_dict()), 201


@org_service.route('settings/members/<string:user_id>', methods=["DELETE"])
@load_user(allow_anonymous=False)
@load_org(
    redirect_to="org_service.remove_member_from_org", allow_anonymous=False)
def remove_member_from_org(user_claim: Dict[str, Any], org: Org,
                           user_id: str):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    # the user making the request
    account_id = user_claim["id"]
    if not org.is_owner(account_id):
        return abort(400)

    user_id = shortuuid.decode(user_id)
    # the user to remove
    account = UserAccount.query.filter(UserAccount.id==user_id).first()
    if not account:
        return "", 204

    if org.is_owner(account.id) and org.has_single_owner():
        return abort(400)

    org.remove_member(user_id)
    db.session.commit()

    record_activity({
        "title": org.name,
        "account_id": account_id,
        "kind": "organization",
        "info": "collaborator removed",
        "org_id": org.id,
        "visibility": ActivityVisibility.authenticated
    })

    return "", 204


@org_service.route('settings/members/<string:user_id>', methods=["PATCH"])
@load_user(allow_anonymous=False)
@load_org(redirect_to="org_service.patch_membership", allow_anonymous=False)
def patch_membership(user_claim: Dict[str, Any], org: Org, user_id: str):
    if request.headers.get('Accept') != 'application/json':
        return render_template('index.html')

    # the user making the request
    account_id = user_claim["id"]
    if not org.is_owner(account_id):
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

    turn_owner = user.get("org_owner", False)
    if turn_owner and org.is_member(account.id):
        org.make_owner(account.id)
    elif not turn_owner and org.is_owner(account.id):
        if org.has_single_owner():
            return abort(400)
        org.make_member(account.id)

    db.session.commit()

    record_activity({
        "title": org.name,
        "account_id": account_id,
        "kind": "organization",
        "info": "collaborator updated",
        "org_id": org.id,
        "visibility": ActivityVisibility.authenticated
    })

    return "", 200
