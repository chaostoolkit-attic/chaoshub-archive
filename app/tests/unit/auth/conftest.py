# -*- coding: utf-8 -*-
from datetime import datetime
import os
from typing import Callable, Dict, List
from unittest.mock import MagicMock, patch

import dateparser
from flask import Flask
from flask_caching import Cache
import pytest

from chaoshubdashboard.app import create_app
from chaoshubdashboard.auth.model import AccessToken, Account, Client, ProviderToken
from chaoshubdashboard.model import db
from chaoshubdashboard.settings import load_settings


@pytest.fixture(scope="session")
def app() -> Flask:
    load_settings(os.path.join(os.path.dirname(__file__), "..", ".env.test"))
    application = create_app(create_tables=False)

    with application.app_context():
        db.create_all(app=application)
    
    return application


@pytest.fixture(scope="session", autouse=True)
def default_dataset(app: Flask):
    client = Client(
        id=1,
        client_id="f5089dc580955311ab7668845183bca7",
        client_secret="619b82b87b70ad7b025dc0fe327b5053230dcd530c329a83366b39404bde",
        account_id="c1337e77-ccaf-41cf-a68c-d6e2026aef21"
    )

    token = ProviderToken(
        id=1,
        name="github",
        client_id="f5089dc580955311ab7668845183bca7",
        token_type="bearer",
        access_token="2e9eee679cd0e739b07f9b1c85e5af300053278d7b946c871b7d3e95a319",
        refresh_token="6ce05d07a6249daa405e82a8bbb7c88f1f9a50a9878b2146d6a9c1bf8804"
    )

    account = Account(
        id="c1337e77-ccaf-41cf-a68c-d6e2026aef21",
        joined_on=dateparser.parse("2018-04-01T18:11:48.681677Z"),
        oauth_provider="github",
        oauth_provider_sub="12345"
    )

    access_token = AccessToken(
        id="127e7132-c3a8-430e-a6c2-220e3b5d7796",
        name="my token",
        access_token="whatever",
        account_id="c1337e77-ccaf-41cf-a68c-d6e2026aef21",
        last_used_on=dateparser.parse("2018-04-01T18:11:48.681677Z"),
        account=account
    )
    account.access_tokens.append(access_token)
    account.client = client

    with app.app_context():
        try:
            db.session.add(access_token)
            db.session.add(token)
            db.session.add(client)
            db.session.add(account)

            db.session.commit()
            db.session.expunge_all()

            yield db
        except:
            db.session.rollback()
        finally:
            db.session.delete(access_token)
            db.session.delete(token)
            db.session.delete(client)
            db.session.delete(account)

            db.session.commit()
            db.session.expunge_all()


@pytest.fixture(scope="function")
def simple_cache(app: Flask):
    return Cache(app, config={'CACHE_TYPE': 'simple'})


@pytest.fixture(scope="function")
def db_envs():
    try:
        os.environ["DB_HOST"] = "localhost"
        os.environ["DB_PORT"] = "5432"
        os.environ["DB_USER"] = "root"
        os.environ["DB_PWD"] = "mypwd"
        os.environ["DB_NAME"] = "mydb"
        yield
    finally:
        os.environ.pop("DB_HOST")
        os.environ.pop("DB_PORT")
        os.environ.pop("DB_USER")
        os.environ.pop("DB_PWD")
        os.environ.pop("DB_NAME")
