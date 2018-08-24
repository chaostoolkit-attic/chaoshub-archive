# -*- coding: utf-8 -*-
import os
from typing import Any, Dict

from flask import current_app, Flask, jsonify
from flask_caching import Cache

from .views import experiment_service
from .views.execution import execution_service
from .views.schedule import schedule_experiment_service
from .views.workspace import workspace_experiment_service

__all__ = ["setup_service"]


def setup_service(main_app: Flask, cache: Cache):
    main_app.register_blueprint(experiment_service, url_prefix="/experiment")
    main_app.register_blueprint(
        workspace_experiment_service,
        url_prefix="/<string:org>/<string:workspace>/experiment")
    main_app.register_blueprint(
        execution_service,
        url_prefix="/<string:org>/<string:workspace>/experiment"
                   "/<string:experiment_id>/execution")
    main_app.register_blueprint(
        schedule_experiment_service,
        url_prefix="/<string:org>/<string:workspace>/experiment"
                   "/<string:experiment_id>/schedule")
