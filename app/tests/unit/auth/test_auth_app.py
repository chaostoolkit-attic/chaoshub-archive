# -*- coding: utf-8 -*-
from flask import Flask
from flask_caching import Cache

from chaoshubdashboard.app import setup_db
from chaoshubdashboard.auth import OAUTH_REMOTE_APPS, OAUTH_BACKENDS
from chaoshubdashboard.auth.app import setup_service
from chaoshubdashboard.model import get_db_conn_uri_from_env


def test_setup_service(simple_cache: Cache):
    app = Flask(__name__)
    setup_service(app, simple_cache)

    assert 'auth_service' in app.blueprints
    bp = app.blueprints['auth_service']
    assert bp.url_prefix is None

    for backend_name in OAUTH_BACKENDS:
        assert backend_name in OAUTH_REMOTE_APPS

    assert 'sqlalchemy' not in app.extensions


def test_get_db_conn_uri_from_env(db_envs):
    db_uri = get_db_conn_uri_from_env()
    assert db_uri == "postgresql://root:mypwd@localhost:5432/mydb"


def test_setup_db(db_envs):
    app = Flask(__name__)
    setup_db(app)

    assert app.config["SQLALCHEMY_ECHO"] is False
    assert app.config["SQLALCHEMY_DATABASE_URI"] == \
        "postgresql://root:mypwd@localhost:5432/mydb"
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False
    assert 'sqlalchemy' in app.extensions
