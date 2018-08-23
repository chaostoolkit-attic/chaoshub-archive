# -*- coding: utf-8 -*-
import time
from unittest.mock import patch

from authlib.specs.oidc import UserInfo as ProfileInfo
from authlib.client.errors import MissingTokenError
from flask import Flask, session
from jose import jwt
import pytest
import shortuuid
import sqlalchemy

from chaoshubdashboard.model import db
from chaoshubdashboard.auth import get_account_by_subject, \
    get_current_user_claim_from_session, register_account, \
    generate_nonce_key, get_oauth_remote_app, get_user_claim, \
    get_user_profile_info_from_oauth, handle_signin, handle_signup, \
    generate_access_token, sign_value, unsign_value, revoke_access_token
from chaoshubdashboard.auth.model import AccessToken, Account, Client, ProviderToken


def test_get_user(app: Flask):
    with app.app_context():
        user = get_account_by_subject("12345", "github")
        assert user is not None
        assert str(user.id) == "c1337e77-ccaf-41cf-a68c-d6e2026aef21"


def test_get_by_unknown_subject(app: Flask):
    with app.app_context():
        user = get_account_by_subject("somesubject", "github")
        assert user is None


def test_get_by_subject(app: Flask):
    with app.app_context():
        user = get_account_by_subject("12345", "github")
        assert user is not None
        assert str(user.id) == "c1337e77-ccaf-41cf-a68c-d6e2026aef21"


def test_get_client_by_user(app: Flask):
    with app.app_context():
        user = get_account_by_subject("12345", "github")
        assert user is not None

        client = Client.query.filter(Client.account_id==user.id).first()
        assert client is not None
        assert str(client.account_id) == "c1337e77-ccaf-41cf-a68c-d6e2026aef21"


def test_current_user_without_session(app: Flask):
    with app.app_context():
        with app.test_request_context():
            user = get_current_user_claim_from_session()
            assert user is None


def test_get_user_with_session_id_set_to_unknown_user_id(app: Flask):
    with app.app_context():
        with app.test_request_context():
            session["sid"] = "c57b5426-3510-4598-987e-3b0534d14395"
            user = get_current_user_claim_from_session()
            assert user is None
            assert "sid" not in session


def test_get_user_with_session_id(app: Flask):
    with app.app_context():
        with app.test_request_context():
            session["sid"] = "c1337e77-ccaf-41cf-a68c-d6e2026aef21"
            claim = get_current_user_claim_from_session()
            assert claim is not None

            user = jwt.decode(claim, app.config.get("CLAIM_SIGNER_KEY"))
            assert str(user["id"]) == "c1337e77-ccaf-41cf-a68c-d6e2026aef21"


def test_register_user(app: Flask):
    with app.app_context():
        users = Account.query.all()
        assert len(users) == 1

        profile = ProfileInfo(
            preferred_username="jane",
            email="jane@beyondthestars.net",
            sub="56789",
            given_name="Jane",
            family_name="Doe"
        )

        user = None
        try:
            with patch('chaoshubdashboard.auth.DashboardService', autospec=False):
                user = register_account(profile, "github")

            users = Account.query.all()
            assert len(users) == 2

            assert user.is_closed is False
            assert user.is_active is True

        finally:
            assert user is not None
            db.session.delete(user)
            db.session.commit()

        users = Account.query.all()
        assert len(users) == 1


def test_register_user_twice_is_forbidden(app: Flask):
    with app.app_context():
        users = Account.query.all()
        assert len(users) == 1

        profile = ProfileInfo(
            preferred_username="jane",
            email="jane@beyondthestars.net",
            sub="56789",
            given_name="Jane",
            family_name="Doe"
        )

        user = None
        try:
            with patch('chaoshubdashboard.auth.DashboardService', autospec=False):
                user = register_account(profile, "github")
                assert user.is_closed is False
                assert user.is_active is True

            users = Account.query.all()
            assert len(users) == 2

            with patch('chaoshubdashboard.auth.DashboardService', autospec=False):
                with pytest.raises(sqlalchemy.exc.IntegrityError):
                    register_account(profile, "github")
        finally:
            assert user is not None
            db.session.rollback()
            db.session.delete(user)
            db.session.commit()

        users = Account.query.all()
        assert len(users) == 1


def test_github_oauth_backend_does_not_generate_nonce_key(app: Flask):
    nonce = generate_nonce_key("github")
    assert nonce is None


def test_gitlab_oauth_backend_does_not_generate_nonce_key(app: Flask):
    nonce = generate_nonce_key("gitlab")
    assert nonce is None


def test_google_oauth_backend_generates_nonce_key(app: Flask):
    with app.app_context():
        with app.test_request_context():
            nonce = generate_nonce_key("google")
            assert len(nonce) == 20
            assert session['_google:nonce'] == nonce


def test_github_is_a_registered_oauth_provider(app: Flask):
    remote = get_oauth_remote_app('github')
    assert remote is not None


def test_gitlab_is_a_registered_oauth_provider(app: Flask):
    remote = get_oauth_remote_app('gitlab')
    assert remote is not None


def test_google_is_a_registered_oauth_provider(app: Flask):
    remote = get_oauth_remote_app('google')
    assert remote is not None


def test_get_profile_from_oauth_fails_when_token_missing(app: Flask):
    with app.app_context():
        remote = get_oauth_remote_app('gitlab')
        with pytest.raises(MissingTokenError):
            get_user_profile_info_from_oauth('gitlab', remote, None)


def test_get_profile_from_oauth_with_unknown_backend(app: Flask):
    profile = get_user_profile_info_from_oauth('whatever', None, None)
    assert profile is None


def test_handle_signin_save_provider_token(app: Flask):
    with app.app_context():
        account = Account.query.filter(
            Account.id=="c1337e77-ccaf-41cf-a68c-d6e2026aef21").first()
        
        with app.test_request_context():
            handle_signin(account, {
                "token_type": "bearer",
                "access_token": "access",
                "refresh_token": "refresh",
                "expires_at": 10
            }, "gitlab")

            assert "sid" in session
            assert session["sid"] == "c1337e77-ccaf-41cf-a68c-d6e2026aef21"
            assert session.permanent is True
            
            tokens = ProviderToken.query.filter(ProviderToken.id!=1).all()
            assert len(tokens) == 1
            db.session.delete(tokens[0])
            db.session.commit()


def test_handle_signin_update_provider_token(app: Flask):
    with app.app_context():
        account = Account.query.filter(
            Account.id=="c1337e77-ccaf-41cf-a68c-d6e2026aef21").first()
        
        with app.test_request_context():
            handle_signin(account, {
                "token_type": "bearer",
                "access_token": "access",
                "refresh_token": "refresh",
                "expires_at": 10
            }, "github")

            assert "sid" in session
            assert session["sid"] == "c1337e77-ccaf-41cf-a68c-d6e2026aef21"
            assert session.permanent is True

            tokens = ProviderToken.query.filter(ProviderToken.id!=1).all()
            assert len(tokens) == 1
            db.session.delete(tokens[0])
            db.session.commit()

            tokens = ProviderToken.query.all()
            assert len(tokens) == 1


def test_handle_signup_create_account(app: Flask):
    with app.app_context():
        profile = ProfileInfo(
            sub="12345",
            name="Jane Doe",
            preferred_username="jane",
            email="jane@doe.org",
        )
        with app.test_request_context():
            account = handle_signup(profile, {
                "token_type": "bearer",
                "access_token": "access",
                "refresh_token": "refresh",
                "expires_at": 10
            }, "gitlab")

            # TODO: is this needed?
            #assert "sid" in session
            #assert session.permanent is True
            
            tokens = ProviderToken.query.filter(ProviderToken.id!=1).all()
            assert len(tokens) == 1
            db.session.delete(tokens[0])
            db.session.delete(account)
            db.session.commit()


def test_get_user_claim_key_must_be_provided(app: Flask):
    try:
        key = app.config.pop("CLAIM_SIGNER_KEY")
        with pytest.raises(RuntimeError):
            get_user_claim(None)
    finally:
        app.config["CLAIM_SIGNER_KEY"] = key


def test_generate_access_token(app: Flask):
    with app.app_context():
        claim = {"id": "c1337e77-ccaf-41cf-a68c-d6e2026aef21"}
        name = "my token"

        token = generate_access_token(claim, name)
        token_id = shortuuid.decode(token["id"])
        access_token = AccessToken.query.filter(
            AccessToken.id==token_id).first()
        assert access_token is not None
        assert access_token.name == name
        assert access_token.token_type == "bearer"
        assert access_token.revoked is False
        assert str(access_token.account_id) == \
            "c1337e77-ccaf-41cf-a68c-d6e2026aef21"

        db.session.delete(access_token)
        db.session.commit()


def test_sign_value(app: Flask):
    with app.app_context():
        value = {"key": "hello"}
        signed_value = sign_value(app, value)
        assert signed_value is not None
        assert isinstance(signed_value, str)


def test_unsign_value(app: Flask):
    with app.app_context():
        value = {"key": "hello"}
        signed_value = sign_value(app, value)
        decoded_value = unsign_value(app, signed_value)
        assert "key" in decoded_value
        assert decoded_value["key"] == "hello"


def test_unsign_value_fails_when_expires(app: Flask):
    with app.app_context():
        value = {"key": "hello"}
        signed_value = sign_value(app, value, expire_in=0)
        time.sleep(1)
        decoded_value = unsign_value(app, signed_value)
        assert decoded_value is None


def test_revoke_access_token(app: Flask):
    with app.app_context():
        token = AccessToken.query.filter(
            AccessToken.id=="127e7132-c3a8-430e-a6c2-220e3b5d7796").first()
        expires_in = token.expires_in

        revoke_access_token(
            "c1337e77-ccaf-41cf-a68c-d6e2026aef21",
            "127e7132-c3a8-430e-a6c2-220e3b5d7796")

        assert token.expires_in == -3600
        assert token.revoked is True

        token.expires_in = expires_in
        token.revoked = False
        db.session.commit()
