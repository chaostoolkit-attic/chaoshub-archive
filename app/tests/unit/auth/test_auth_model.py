# -*- coding: utf-8 -*-
import uuid 

import dateparser
import pytest
import shortuuid

from chaoshubdashboard.model import db
from chaoshubdashboard.auth.model import Account, AccessToken, Client, \
    ProviderToken


def test_can_fetch_account(default_dataset):
    account = Account.query.filter(
        Account.id=="c1337e77-ccaf-41cf-a68c-d6e2026aef21").first()

    assert account is not None
    assert account.is_closed is False
    assert account.is_active is True
    assert account.joined_on == dateparser.parse("2018-04-01T18:11:48.681677")
    assert account.closed_since is None
    assert account.inactive_since is None
    assert account.oauth_provider == "github"
    assert account.oauth_provider_sub == "12345"


def test_account_to_dict(default_dataset):
    account = Account.query.filter(
        Account.id=="c1337e77-ccaf-41cf-a68c-d6e2026aef21").first()
    d = account.to_dict()

    assert "id" in d
    assert d["id"] == "c1337e77-ccaf-41cf-a68c-d6e2026aef21"
    assert "closed" in d
    assert d["closed"] is False
    assert "active" in d
    assert d["active"] is True
    assert "joined_on" in d
    assert d["joined_on"] == "2018-04-01T18:11:48.681677Z"
    assert "inactive_since" in d
    assert d["inactive_since"] is None
    assert "closed_since" in d
    assert d["closed_since"] is None
    assert "tokens" in d
    assert "client" in d

    account.turn_inactive()
    d = account.to_dict()
    assert "inactive_since" in d
    assert dateparser.parse(d["inactive_since"].replace('Z', '')) == \
        account.inactive_since

    account.close_account()
    d = account.to_dict()
    assert "closed_since" in d
    assert dateparser.parse(d["closed_since"].replace('Z', '')) == \
        account.closed_since

    account.turn_active()


def test_can_create_and_delete_account(default_dataset):
    account = Account(
        id="6570ee44-6a86-4f3e-9899-88a55be849c1",
        joined_on=dateparser.parse("2018-07-01T18:11:48.681677Z"),
        oauth_provider="gitlab",
        oauth_provider_sub="12348"
    )
    try:
        db.session.add(account)
        db.session.commit()
    except:
        pytest.fail("Failed to create account")
    finally:
        try:
            db.session.delete(account)
            db.session.commit()
        except:
            pytest.fail("Failed to delete account")
        finally:
            account = Account.query.filter(
                Account.id=="6570ee44-6a86-4f3e-9899-88a55be849c1").first()
            assert account is None


def test_can_fetch_access_token(default_dataset):
    token = AccessToken.query.filter(
        AccessToken.id=="127e7132-c3a8-430e-a6c2-220e3b5d7796").first()
    assert token is not None
    assert token.access_token == "whatever"
    assert str(token.account_id) == "c1337e77-ccaf-41cf-a68c-d6e2026aef21"


def test_can_fetch_access_token_by_account_id(default_dataset):
    token = AccessToken.query.filter(
        AccessToken.account_id=="c1337e77-ccaf-41cf-a68c-d6e2026aef21").first()
    assert token is not None
    assert token.access_token == "whatever"
    assert token.last_used_on == dateparser.parse("2018-04-01T18:11:48.681677")
    assert str(token.account_id) == "c1337e77-ccaf-41cf-a68c-d6e2026aef21"


def test_access_token_to_dict(default_dataset):
    token = AccessToken.query.filter(
        AccessToken.id=="127e7132-c3a8-430e-a6c2-220e3b5d7796").first()
    d = token.to_dict()

    assert "id" in d
    assert d["id"] == shortuuid.encode(
        uuid.UUID("127e7132-c3a8-430e-a6c2-220e3b5d7796"))
    assert "name" in d
    assert d["name"] == "my token"
    assert "access_token" in d
    assert d["access_token"] == "whatever"
    assert "last_used" in d
    assert d["last_used"] == "2018-04-01T18:11:48.681677Z"


def test_can_create_and_delete_access_token(default_dataset):
    token = AccessToken(
        id="223a1803-740d-4cd8-a832-295a37206a70",
        name="my token",
        access_token="whatever again",
        account_id="c1337e77-ccaf-41cf-a68c-d6e2026aef21"
    )
    try:
        db.session.add(token)
        db.session.commit()
    except:
        pytest.fail("Failed to create token")
    finally:
        try:
            db.session.delete(token)
            db.session.commit()
        except:
            pytest.fail("Failed to delete token")
        finally:
            token = AccessToken.query.filter(
                AccessToken.id=="223a1803-740d-4cd8-a832-295a37206a70").first()
            assert token is None


def test_can_create_and_delete_provider_token(default_dataset):
    token = ProviderToken(
        id=20000,
        name="gitlab",
        client_id="g6089dc580955311ab7668845183bca7",
        token_type="bearer",
        access_token="5y9eee679cd0e739b07f9b1c85e5af300053278d7b946c871b7d3e95a319",
        refresh_token="3oe05d07a6249daa405e82a8bbb7c88f1f9a50a9878b2146d6a9c1bf8804"
    )
    try:
        db.session.add(token)
        db.session.commit()
    except:
        pytest.fail("Failed to create provider token")
    finally:
        try:
            db.session.delete(token)
            db.session.commit()
        except:
            pytest.fail("Failed to delete provider token")
        finally:
            token = ProviderToken.query.filter(ProviderToken.id==20000).first()
            assert token is None


def test_provider_token_to_dict(default_dataset):
    token = ProviderToken.query.filter(ProviderToken.id==1).first()
    d = token.to_dict()

    assert d["id"] == 1
    assert d["access_token"] == "2e9eee679cd0e739b07f9b1c85e5af300053278d7b946c871b7d3e95a319"
    assert d["token_type"] == "bearer"
    assert d["revoked"] is False
    assert d["refresh_token"] == "6ce05d07a6249daa405e82a8bbb7c88f1f9a50a9878b2146d6a9c1bf8804"


def test_can_create_and_delete_client(default_dataset):
    account = Account(
        id="6570ee44-6a86-4f3e-9899-88a55be849c1",
        joined_on=dateparser.parse("2018-07-01T18:11:48.681677Z"),
        oauth_provider="gitlab",
        oauth_provider_sub="12348"
    )
    client = Client(
        id=10000,
        client_id="a5089dc580955311ab7668845183bca7",
        client_secret="a19b82b87b70ad7b025dc0fe327b5053230dcd530c329a83366b39404bde",
        account_id="6570ee44-6a86-4f3e-9899-88a55be849c1"
    )
    try:
        db.session.add(account)
        db.session.add(client)
        db.session.commit()
    except:
        pytest.fail("Failed to create client")
    finally:
        try:
            db.session.delete(account)
            db.session.delete(client)
            db.session.commit()
        except:
            pytest.fail("Failed to delete client")
        finally:
            client = Client.query.filter(Client.id==10000).first()
            assert client is None


def test_client_to_dict(default_dataset):
    token = Client.query.filter(Client.id==1).first()
    d = token.to_dict()

    assert d["id"] == 1
    assert d["client_id"] == "f5089dc580955311ab7668845183bca7"
    assert d["client_secret"] == \
        "619b82b87b70ad7b025dc0fe327b5053230dcd530c329a83366b39404bde"
