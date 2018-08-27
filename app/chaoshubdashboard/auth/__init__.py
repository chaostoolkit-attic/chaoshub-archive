# -*- coding: utf-8 -*-
from calendar import timegm
from copy import deepcopy
from datetime import datetime, timedelta
from functools import wraps
import secrets
import time
from typing import Any, Dict, List, Optional

from authlib.common.security import generate_token
from authlib.flask.client import OAuth, RemoteApp
from authlib.flask.oauth2 import current_token, ResourceProtector
from authlib.specs.oidc import UserInfo as ProfileInfo
from dateparser import parse
from flask import abort, current_app, Flask, g, jsonify, redirect, request, \
    session, url_for
from flask_caching import Cache
import itsdangerous
from itsdangerous import TimestampSigner
from jose import jwt
from loginpass import Bitbucket, Google, Gitlab, GitHub
from loginpass._core import register_to

from .model import Account, Client, ProviderToken, AccessToken, LocalAccount
from .services import DashboardService, APIService
from .types import UserClaim
from ..model import db

__all__ = ["fetch_token_info", "get_user_claim", "get_active_access_tokens",
           "register_account", "update_provider_token", "get_access_token",
           "fully_delete_user_info", "sign_value", "get_account_by_subject",
           "unsign_value", "handle_signin_authorize",
           "handle_signup_authorize", "setup_oauth_backends",
           "get_oauth_remote_app", "generate_nonce_key", "log_user_in",
           "get_user_profile_info_from_oauth", "handle_signin",
           "handle_signup", "revoke_access_token", "register_local_account",
           "get_current_user_claim_from_session", "update_access_token"]


OAUTH_BACKENDS = {
    Google.OAUTH_NAME: Google,
    GitHub.OAUTH_NAME: GitHub,
    Gitlab.OAUTH_NAME: Gitlab,
    Bitbucket.OAUTH_NAME: Bitbucket
}
OAUTH_REMOTE_APPS = dict()


def setup_oauth_backends(main_app: Flask, cache: Cache) -> OAuth:
    """
    Configure the OAuth2 service providers.
    """
    oauth = OAuth(main_app, cache=cache)
    for backend in OAUTH_BACKENDS.values():
        remote = register_to(backend, oauth, RemoteApp)
        OAUTH_REMOTE_APPS[backend.OAUTH_NAME] = remote
    return oauth


def get_oauth_remote_app(oauth_provider: str) -> RemoteApp:
    """
    Lookup the application for the given provider
    """
    return OAUTH_REMOTE_APPS.get(oauth_provider)


def generate_nonce_key(oauth_provider: str) -> Optional[str]:
    """
    Generate a nonce key for OpenID aware providers.
    """
    backend = OAUTH_BACKENDS.get(oauth_provider)
    if backend and 'oidc' in backend.OAUTH_TYPE:
        nonce_key = '_{}:nonce'.format(backend.OAUTH_NAME)
        nonce = generate_token(20)
        session[nonce_key] = nonce
        return nonce

    return None


def get_account_by_subject(sub: str, provider: str) -> Account:
    """
    Lookup an account by its OpenID subject which is unique for a provider.
    """
    return Account.query.filter(
        Account.oauth_provider==provider,
        Account.oauth_provider_sub==sub).first()


def get_user_profile_info_from_oauth(oauth_provider: str, remote: RemoteApp,
                                     token: Dict[str, str]) -> ProfileInfo:
    """
    Load the user profile from the OAuth backend service using the given token.
    """
    backend = OAUTH_BACKENDS.get(oauth_provider)
    if not backend:
        return None

    if token and 'id_token' in token:
        nonce_key = '_{}:nonce'.format(backend.OAUTH_NAME)
        nonce = session.get(nonce_key)
        if not nonce:
            return None
        user_info = remote.parse_openid(token, nonce)
    else:
        user_info = remote.profile()

    return user_info


def handle_signin(account: Account, token: Dict[str, str],
                  oauth_provider: str):
    update_provider_token(oauth_provider, account, token)
    session['sid'] = str(account.id)
    session.permanent = True
    current_app.logger.info("User logged in: {}".format(str(account.id)))


def handle_signup(user_info: ProfileInfo, token: Dict[str, str],
                  oauth_provider: str) -> Account:
    account = register_account(user_info, oauth_provider)
    update_provider_token(oauth_provider, account, token)
    current_app.logger.info("User created: {}".format(str(account.id)))
    return account


def get_current_user_claim_from_session() -> Optional[str]:
    """
    Return a signed claim representing the currently logged in user.
    """
    sid = session.get('sid')
    if not sid:
        return None

    account = Account.query.filter(Account.id==sid).first()
    if not account:
        session.pop('sid', None)
        return None

    return get_user_claim(account)


def get_user_claim(account: Account) -> Optional[str]:
    """
    Return a signed claim representing the given user.
    """
    key = current_app.config.get("CLAIM_SIGNER_KEY")
    if not key:
        raise RuntimeError("CLAIM_SIGNER_KEY is empty or missing")
    d = account.to_dict()
    return encode_as_jwt(d, key)


def register_local_account(username: str, password: str) -> Optional[Account]:
    """
    Create a new local account from a username/password pair.
    """
    lower_username = username.lower()
    local = LocalAccount.query.filter(
        LocalAccount.username==lower_username).first()
    if local:
        return None

    client = Client(
        client_id=secrets.token_hex(16),
        client_secret=secrets.token_hex(30))
    db.session.add(client)

    local = LocalAccount(username=lower_username, password=password)
    db.session.add(local)

    account = Account(
        local=local,
        client=client,
        joined_on=datetime.utcnow())
    local.account_id = account.id
    db.session.add(account)

    db.session.commit()

    user_claim = account.to_dict()

    profile = {
        "preferred_username": username,
        "name": username
    }
    DashboardService.register_new_user(user_claim, profile)

    return account


def log_user_in(username: str, password: str) -> Optional[Account]:
    local = LocalAccount.query.filter(
        LocalAccount.username==username.lower()).first()

    if not local or local.password != password:
        return None
    return Account.query.filter(Account.id==local.account_id).first()


def register_account(profile: ProfileInfo, oauth_provider: str) -> Account:
    """
    Create a new account from a OpenID user description as well as a Client
    id/secret pair for that user.

    .. seealso:
        http://openid.net/specs/openid-connect-basic-1_0-28.html#userinfo
    """
    client = Client(
        client_id=secrets.token_hex(16),
        client_secret=secrets.token_hex(30))
    db.session.add(client)

    account = Account(
        client=client,
        joined_on=datetime.utcnow(),
        oauth_provider=oauth_provider,
        oauth_provider_sub=profile.sub)

    db.session.add(account)
    db.session.commit()

    user_claim = account.to_dict()

    DashboardService.register_new_user(user_claim, profile)

    return account


def update_provider_token(name: str, account: Account,
                          token: Dict[str, str]) -> ProviderToken:
    """
    Update the provider token for the given user.
    """
    item = ProviderToken.query.filter_by(
        name=name, account_id=account.id).first()
    if not item:
        item = ProviderToken(name=name, account_id=account.id)
    item.token_type = token.get('token_type', 'bearer')
    item.access_token = token.get('access_token')
    item.refresh_token = token.get('refresh_token')
    item.expires_at = token.get('expires_at')
    db.session.add(item)
    db.session.commit()
    return item


def get_access_token(user_claim: UserClaim,
                     token_id: str) -> Optional[Dict[str, Any]]:
    token = AccessToken.query.filter(AccessToken.id==token_id).first()
    if token:
        return token.to_dict()
    return None


def get_active_access_tokens(user_claim: UserClaim) -> List[Dict[str, Any]]:
    account_id = user_claim["id"]
    tokens = AccessToken.query.filter(
        AccessToken.account_id==account_id,
        AccessToken.revoked==False).all()
    return [token.to_dict() for token in tokens]


def generate_access_token(user_claim: Dict[str, Any], name: str,
                          expire_in: str = "in 5 years") -> Dict[str, Any]:
    """
    Create an access token for the given account.
    """
    account_id = user_claim['id']
    client = Client.query.filter(Client.account_id==account_id).first()
    expires_in = int((parse(expire_in) - datetime.utcnow()).total_seconds())

    token = AccessToken(
        name=name,
        client_id=client.client_id,
        access_token=secrets.token_hex(30),
        refresh_token=secrets.token_hex(30),
        account_id=account_id,
        expires_in=expires_in,
        token_type="bearer"
    )
    db.session.add(token)
    db.session.commit()

    access_token = token.to_dict()
    APIService.set_access_token(access_token)

    return access_token


def revoke_access_token(account_id: str, token_id: str):
    """
    Revoke an access token for the given user.
    """
    token = AccessToken.query.filter(
        AccessToken.id==token_id, AccessToken.account_id==account_id).first()
    if token:
        token.expires_in = -3600
        token.revoked = True
        db.session.commit()

        APIService.revoke_access_token(token)


def update_access_token(access_token: Dict[str, Any]):
    """
    Update the access token with this new content
    """
    token = AccessToken.query.filter(
        AccessToken.access_token==access_token["access_token"],
        AccessToken.account_id==access_token["account_id"]).first()
    if token:
        token.last_used_on = datetime.utcfromtimestamp(
            access_token["last_used"])
        db.session.commit()


def encode_as_jwt(payload: Dict[str, Any], secret_key: str,
                  expire_in: int = 60) -> str:
    """
    Encode the given data in a JWT payload.
    """
    payload = deepcopy(payload)
    now = datetime.utcnow()
    payload["iat"] = now
    payload["nbf"] = now
    payload["exp"] = now + timedelta(seconds=expire_in)
    return jwt.encode(payload, secret_key, algorithm='HS384')


def sign_value(app: Flask, value: Dict[str, Any], expire_in: int = 60) -> str:
    """
    Sign (with a timestamp) the given value.
    """
    sign_key = app.config.get("SIGNER_KEY")
    return encode_as_jwt(value, sign_key, expire_in)


def unsign_value(app: Flask, signed_value: str) -> Optional[Dict[str, Any]]:
    """
    Sign (with a timestamp) the given value. It cannot be older than `max_age`.
    """
    sign_key = app.config.get("SIGNER_KEY")
    try:
        decoded = jwt.decode(signed_value, sign_key, algorithms='HS384')
    except Exception as x:
        app.logger.error(
            "Failed to unsign {}".format(signed_value), exc_info=x)
        return None

    exp = decoded["exp"]
    now = datetime.utcnow()
    if timegm(now.utctimetuple()) > exp:
        app.logger.error("Signed value has expired: {}".format(signed_value))
        return None

    return decoded
