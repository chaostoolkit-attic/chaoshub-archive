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
def app() -> Flask:
    load_settings(os.path.join(os.path.dirname(__file__), ".env.test"))
    application = create_app()
    return application


@pytest.fixture(scope="session")
def cache(app: Flask) -> Cache:
    return Cache(app, config={'CACHE_TYPE': 'simple'})
