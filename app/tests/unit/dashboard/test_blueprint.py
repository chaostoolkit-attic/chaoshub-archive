# -*- coding: utf-8 -*-
import os
import os.path
from unittest.mock import patch

import cherrypy
from flask import Flask
from flask_caching import Cache

from chaoshubdashboard.app import setup_db
from chaoshubdashboard.model import db, get_db_conn_uri_from_env
from chaoshubdashboard.settings import load_settings


def test_get_db_conn_uri_from_env():
    try:
        os.environ.update({
            "DB_HOST": "192.168.1.10",
            "DB_PORT": "5432",
            "DB_USER": "user",
            "DB_PWD": "pwd",
            "DB_NAME": "chaos"
        })
        uri = get_db_conn_uri_from_env()

        assert uri == "postgresql://user:pwd@192.168.1.10:5432/chaos"
    finally:
        os.environ.pop("DB_HOST")
        os.environ.pop("DB_PORT")
        os.environ.pop("DB_USER")
        os.environ.pop("DB_PWD")
        os.environ.pop("DB_NAME")


@patch('chaoshubdashboard.app.get_db_conn_uri_from_env', autospec=False)
def test_setup_db(get_db_conn_uri_from_env):
    load_settings(os.path.join(os.path.dirname(__file__), "..", ".env.test"))
    get_db_conn_uri_from_env.return_value = os.getenv("DB_HOST")

    app = Flask(__name__)

    with app.app_context():
        app.config["SQLALCHEMY_ECHO"] = True if os.getenv("DB_DEBUG") else False
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = get_db_conn_uri_from_env()
        app.config["SQLALCHEMY_BINDS"] = {
            'dashboard_service': app.config["SQLALCHEMY_DATABASE_URI"]
        }
        db.init_app(app)
        engine = db.get_engine(app, bind='dashboard_service')
        assert engine.dialect.has_table(engine, "user_account") is False

    setup_db(app)

    with app.app_context():
        db.create_all(bind='dashboard_service')
        engine = db.get_engine(app, bind='dashboard_service')
        assert engine.dialect.has_table(engine, "user_account")

        db.drop_all(bind='dashboard_service')
