# -*- coding: utf-8 -*-
import os.path
from unittest.mock import MagicMock, patch

import dateparser
from flask import Flask
from flask_caching import Cache
import pytest

from chaoshubdashboard.app import create_app
from chaoshubdashboard.settings import load_settings


@pytest.fixture(scope="session")
@patch('chaoshubdashboard.app.get_db_conn_uri_from_env', autospec=False)
def app(get_db_conn_uri_from_env) -> Flask:
    load_settings(os.path.join(os.path.dirname(__file__), ".env.test"))
    get_db_conn_uri_from_env.return_value = os.getenv("DB_HOST")
    application = create_app()
    return application


@pytest.fixture(scope="session")
def cache(app: Flask) -> Cache:
    return Cache(app, config={'CACHE_TYPE': 'simple'})
