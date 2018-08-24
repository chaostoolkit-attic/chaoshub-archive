# -*- coding: utf-8 -*-
import os
from typing import Any, Dict

from authlib.flask.oauth2 import ResourceProtector
from authlib.flask.oauth2.sqla import create_bearer_token_validator
from flask import current_app, Flask, jsonify
from flask_caching import Cache

from .model import db, APIAccessToken
from .views import api

__all__ = ["setup_service"]


def setup_service(main_app: Flask, cache: Cache, init_db: bool = True):
    main_app.register_blueprint(
        api, url_prefix='/api/<string:org>/<string:workspace>/experiment')
    setup_oauth2_resource_protector(main_app)


###############################################################################
# Internals
###############################################################################
def setup_oauth2_resource_protector(main_app: Flask):
    """
    Configure OAuth2 endpoints protector
    """
    BearerTokenValidator = create_bearer_token_validator(
        db.session, APIAccessToken)
    ResourceProtector.register_token_validator(BearerTokenValidator())
