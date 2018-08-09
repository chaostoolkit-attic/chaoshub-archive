# -*- coding: utf-8 -*-
import os
from typing import Any, Dict

from flask import Flask, jsonify
from flask_caching import Cache

from . import setup_oauth_backends
from .views import auth_service

__all__ = ["setup_service"]


def setup_service(main_app: Flask, cache: Cache):
    """
    Setup the auth service
    """
    main_app.register_blueprint(auth_service, url_prefix="/auth")
    setup_oauth_backends(main_app, cache)
