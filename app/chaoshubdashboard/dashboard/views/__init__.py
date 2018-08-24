# -*- coding: utf-8 -*-
import os.path
from typing import Any, Dict

from authlib.client.errors import OAuthException
from flask import abort, Blueprint, current_app, jsonify, redirect, \
    render_template, request, session, url_for
import shortuuid
from sqlalchemy import or_

from chaoshubdashboard.utils import get_user_claim, load_user

from .. import get_account_activities, lookup_users
from ..services import ExperimentService
from ..model import Org, UserAccount, UserInfo, Workspace
from ..types import UserClaim

__all__ = ["dashboard_service"]

dashboard_service = Blueprint("dashboard_service", __name__)


@dashboard_service.route('/', defaults={'path': ''}, methods=["GET", "HEAD"])
@dashboard_service.route('/<path:path>', methods=["GET", "HEAD"])
@load_user(allow_anonymous=True)
def index(user_claim: Dict[str, Any], path: str) -> str:
    if user_claim:
        return render_template('index.html')

    return render_template('landing.html')


@dashboard_service.route('/dashboard', methods=["GET", "HEAD"])
@load_user(allow_anonymous=False)
def dashboard(user_claim: Dict[str, Any]) -> str:
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    account_id = user_claim["id"]
    account = UserAccount.query.filter(UserAccount.id==account_id).first()
    if not account:
        return abort(404)

    caller = account.to_short_dict()
    org = account.personal_org
    activities = get_account_activities(account.id, caller)
    exps = ExperimentService.get_user_last_experiments(user_claim)
    info = {
        "requested_by": caller,
        "activities": activities,
        "experiments": exps
    }
    info.update(account.to_public_dict())

    return jsonify(info)


@dashboard_service.route('/status/live', methods=["GET", "HEAD"])
def status_live() -> str:
    return "OK"


@dashboard_service.route('/status/health', methods=["GET", "HEAD"])
def status_health() -> str:
    return "OK"


@dashboard_service.route('/signout')
@load_user(allow_anonymous=False)
def signout(user_claim: UserClaim):
    session.pop('sid', None)
    return redirect(current_app.config.get("OAUTH_REDIRECT_BASE"))


@dashboard_service.route('/signup', methods=["GET"])
def signup():
    return render_template('index.html')


@dashboard_service.route('/signin', methods=["GET"])
def signin() -> str:
    return render_template('index.html')


@dashboard_service.route('/signed', methods=["GET"])
@load_user(allow_anonymous=True)
def signed(user_claim: UserClaim) -> str:
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    return jsonify(user_claim is not None)


@dashboard_service.route('users/lookup', methods=["GET"])
@load_user(allow_anonymous=False)
def find_member(user_claim: UserClaim):
    if request.headers.get('Accept') != 'application/json':
        return abort(405)

    return jsonify(lookup_users(request.args.get("user")))
