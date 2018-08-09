# -*- coding: utf-8 -*-
from functools import wraps
from typing import Any, Dict, Optional

from flask import abort, current_app, redirect
from jose import jwt
from jose.exceptions import JOSEError
from flask_caching import Cache

from .model import db
from .auth import get_current_user_claim_from_session
from .auth.model import Account, ProviderToken

__all__ = ["get_user_claim", "cache", "load_user"]

cache = Cache()


def load_user(allow_anonymous: bool = False):
    def wrapped(f):
        """
        Decorate views that require the user to be authenticated to access it
        and inject the user's claim into the call.

        Otherwise, automatically redirect to the signin page.
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            signed_account_claim = get_current_user_claim_from_session()
            if not signed_account_claim and not allow_anonymous:
                signin_url = "{}/signin".format(
                    current_app.config.get("OAUTH_REDIRECT_BASE"))
                raise abort(redirect(signin_url))

            kwargs['user_claim'] = None
            if signed_account_claim:
                secret = current_app.config.get("CLAIM_SIGNER_KEY")
                if not secret:
                    raise abort(500)

                try:
                    signed_claim = jwt.decode(
                        signed_account_claim, key=secret, algorithms='HS384')
                except JOSEError as x:
                    raise abort(500)

                kwargs['user_claim'] = signed_claim

            return f(*args, **kwargs)
        return decorated
    return wrapped


def get_user_claim():
    signed_account_claim = get_current_user_claim_from_session()
    if not signed_account_claim:
        return None

    secret = current_app.config.get("CLAIM_SIGNER_KEY")
    if not secret:
        return abort(500)

    try:
        signed_claim = jwt.decode(
            signed_account_claim, key=secret, algorithms='HS384')
    except JOSEError as x:
        return None

    return signed_claim
