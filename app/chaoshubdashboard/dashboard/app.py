# -*- coding: utf-8 -*-
import os
from typing import Any, Dict

from flask import Flask, jsonify, render_template
from flask_caching import Cache

from .views import dashboard_service
from .views.account import account_service
from .views.org import org_service
from .views.workspace import workspace_service

__all__ = ["setup_service"]


def setup_service(main_app: Flask, cache: Cache):
    main_app.register_blueprint(dashboard_service, url_prefix="/")
    main_app.register_blueprint(account_service, url_prefix="/account")
    main_app.register_blueprint(org_service, url_prefix="/<string:org>")
    main_app.register_blueprint(
        workspace_service, url_prefix="/<string:org>/<string:workspace>")

    set_error_pages(main_app)


###############################################################################
# Internals
###############################################################################
def set_error_pages(main_app: Flask):
    @main_app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
