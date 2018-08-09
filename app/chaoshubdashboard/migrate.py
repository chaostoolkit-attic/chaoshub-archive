# -*- coding: utf-8 -*-
import os.path

from flask import Flask
from flask_migrate import Migrate

from .model import db
from .app import create_app
from .settings import load_settings

__all__ = ["migrate_db"]


def migrate_db(env_file: str = '.env') -> Flask:
    """
    Initialize a context for database migration operations.
    """
    env_file = os.path.normpath(
        os.path.join(os.path.dirname(__file__), env_file))
    load_settings(env_file)
    app = create_app()
    migrate = Migrate(app, db, compare_type=True)
    return app
