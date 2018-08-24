# -*- coding: utf-8 -*-
import os.path

from authlib.client.errors import OAuthException
from flask import abort, Blueprint, current_app, redirect, render_template, \
    request, session, url_for, jsonify
from flask_accept import accept
import simplejson as json
from werkzeug.wrappers import Response

from . import generate_nonce_key, get_oauth_remote_app, handle_signin, \
    handle_signup, get_account_by_subject, get_user_profile_info_from_oauth, \
    register_local_account, sign_value, unsign_value, log_user_in
from .services import DashboardService

__all__ = ["auth_service"]

auth_service = Blueprint("auth_service", __name__)


@auth_service.route('signup/local', methods=["POST"])
@accept("application/json")
def signup_local() -> Response:
    payload = request.json

    username = payload.get("username")
    if not username or not username.strip():
        r = jsonify({
            "field": None,
            "message": "Please specify a username"
        })
        r.status_code = 400
        return abort(r)

    password = payload.get("password")
    if not password or not password.strip():
        r = jsonify({
            "field": None,
            "message": "Please specify a password"
        })
        r.status_code = 400
        return abort(r)

    account = register_local_account(username, password)
    if not account:
        r = jsonify({
            "field": "username",
            "message": "Username not available"
        })
        r.status_code = 400
        return abort(r)

    session['sid'] = str(account.id)
    session.permanent = True
    current_app.logger.info("User signed up: {}".format(str(account.id)))

    return "", 200


@auth_service.route('signin/local', methods=["POST"])
@accept("application/json")
def signin_local() -> Response:
    payload = request.json

    username = payload.get("username")
    if not username or not username.strip():
        r = jsonify({
            "field": None,
            "message": "Please specify your username"
        })
        r.status_code = 400
        return abort(r)

    password = payload.get("password")
    if not password or not password.strip():
        r = jsonify({
            "field": None,
            "message": "Please specify your password"
        })
        r.status_code = 400
        return abort(r)

    account = log_user_in(username, password)
    if not account:
        r = jsonify({
            "field": None,
            "message": "Failed to log you in"
        })
        r.status_code = 400
        return abort(r)

    session['sid'] = str(account.id)
    session.permanent = True
    current_app.logger.info("User signed in: {}".format(str(account.id)))

    return "", 200


@auth_service.route('signin/with/<provider>', methods=["GET"])
def signin_with(provider: str) -> Response:
    remote = get_oauth_remote_app(provider)
    if not remote:
        return abort(404)

    params = {
        "state": sign_value(current_app, {
            "via": "signin"
        })
    }
    nonce = generate_nonce_key(provider)
    if nonce:
        params["nonce"] = nonce

    redirect_uri = url_for('.authed', provider=provider, _external=True)
    return remote.authorize_redirect(redirect_uri, **params)


@auth_service.route('signup/with/<provider>', methods=["GET"])
def signup_with(provider: str) -> Response:
    remote = get_oauth_remote_app(provider)
    if not remote:
        return abort(404)

    params = {
        "state": sign_value(current_app, {
            "via": "signup"
        })
    }
    nonce = generate_nonce_key(provider)
    if nonce:
        params["nonce"] = nonce

    redirect_uri = url_for('.authed', provider=provider, _external=True)
    return remote.authorize_redirect(redirect_uri, **params)


@auth_service.route('allowed/via/<provider>', methods=["GET", "POST"])
def authed(provider: str) -> Response:
    signed_state = request.args.get("state")
    if not signed_state:
        return abort(400)

    state = unsign_value(current_app, signed_state)
    if not state:
        return abort(400)

    if 'via' not in state:
        return abort(400)

    via = state['via']
    if via not in ["signin", "signup"]:
        return abort(400)

    remote = get_oauth_remote_app(provider)
    if not remote:
        return abort(404)

    token = None
    id_token = request.args.get('id_token')
    if request.args.get('code'):
        try:
            token = remote.authorize_access_token()
        except OAuthException as x:
            session.pop('sid', None)
            return redirect("/")

        if id_token:
            token['id_token'] = id_token
    elif id_token:
        token = {'id_token': id_token}
    else:
        return redirect("/")

    user_info = get_user_profile_info_from_oauth(provider, remote, token)
    account = get_account_by_subject(user_info.sub, provider)

    if via == "signin":
        if not account:
            return redirect("/signup")
        handle_signin(account, token, provider)

    elif via == "signup":
        if account:
            return redirect("/signin")
        handle_signup(user_info, token, provider)

    return redirect("/", code=303)
