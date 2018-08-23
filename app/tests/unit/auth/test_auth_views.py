# -*- coding: utf-8 -*-
from unittest.mock import patch
from urllib.parse import urlparse, parse_qs

from authlib.specs.oidc import UserInfo as ProfileInfo
from flask import Flask
import pytest
from werkzeug import exceptions

from chaoshubdashboard.auth import generate_nonce_key, sign_value, unsign_value
from chaoshubdashboard.auth.model import Account
from chaoshubdashboard.auth.views import authed, signin_with, signup_with


def test_cannot_signin_with_unknown_provider(app: Flask):
    with app.app_context():
        with app.test_request_context('/auth/signin/with/whatever'):
            with pytest.raises(exceptions.NotFound):
                signin_with('whatever')


def test_signin_with_google(app: Flask):
    with patch("authlib.flask.client.oauth.session", new={}) as sess:
        with app.app_context():
            with app.test_request_context('/auth/signin/with/google'):
                resp = signin_with('google')
                assert resp.status_code == 302
                p = urlparse(resp.location)
                q = parse_qs(p.query)
                assert q['response_type'] == ['code']
                assert q['client_id'] == ['None']
                assert q['scope'] == ['openid email profile']

                p = urlparse(q['redirect_uri'][0])
                assert p.path == '/auth/allowed/via/google'

                assert '_google_state_' in sess
                state = unsign_value(app, sess['_google_state_'])
                assert 'via' in state
                assert state['via'] == 'signin'


def test_signin_with_github(app: Flask):
    with patch("authlib.flask.client.oauth.session", new={}) as sess:
        with app.app_context():
            with app.test_request_context('/auth/signin/with/github'):
                resp = signin_with('github')
                assert resp.status_code == 302
                p = urlparse(resp.location)
                q = parse_qs(p.query)
                assert q['response_type'] == ['code']
                assert q['client_id'] == ['None']
                assert q['scope'] == ['user:email']

                p = urlparse(q['redirect_uri'][0])
                assert p.path == '/auth/allowed/via/github'

                assert '_github_state_' in sess
                state = unsign_value(app, sess['_github_state_'])
                assert 'via' in state
                assert state['via'] == 'signin'


def test_signin_with_gitlab(app: Flask):
    with patch("authlib.flask.client.oauth.session", new={}) as sess:
        with app.app_context():
            with app.test_request_context('/auth/signin/with/gitlab'):
                resp = signin_with('gitlab')
                assert resp.status_code == 302
                p = urlparse(resp.location)
                q = parse_qs(p.query)
                assert q['response_type'] == ['code']
                assert q['client_id'] == ['None']
                assert q['scope'] == ['read_user']

                p = urlparse(q['redirect_uri'][0])
                assert p.path == '/auth/allowed/via/gitlab'

                assert '_gitlab_state_' in sess
                state = unsign_value(app, sess['_gitlab_state_'])
                assert 'via' in state
                assert state['via'] == 'signin'


def test_cannot_signup_with_unknown_provider(app: Flask):
    with app.app_context():
        with app.test_request_context('/auth/signup/with/whatever'):
            with pytest.raises(exceptions.NotFound):
                signup_with('whatever')


def test_signup_with_google(app: Flask):
    with patch("authlib.flask.client.oauth.session", new={}) as sess:
        with app.app_context():
            with app.test_request_context('/auth/signup/with/google'):
                resp = signup_with('google')
                assert resp.status_code == 302
                p = urlparse(resp.location)
                q = parse_qs(p.query)
                assert q['response_type'] == ['code']
                assert q['client_id'] == ['None']
                assert q['scope'] == ['openid email profile']

                p = urlparse(q['redirect_uri'][0])
                assert p.path == '/auth/allowed/via/google'

                assert '_google_state_' in sess
                state = unsign_value(app, sess['_google_state_'])
                assert 'via' in state
                assert state['via'] == 'signup'


def test_signup_with_github(app: Flask):
    with patch("authlib.flask.client.oauth.session", new={}) as sess:
        with app.app_context():
            with app.test_request_context('/auth/signup/with/github'):
                resp = signup_with('github')
                assert resp.status_code == 302
                p = urlparse(resp.location)
                q = parse_qs(p.query)
                assert q['response_type'] == ['code']
                assert q['client_id'] == ['None']
                assert q['scope'] == ['user:email']

                p = urlparse(q['redirect_uri'][0])
                assert p.path == '/auth/allowed/via/github'

                assert '_github_state_' in sess
                state = unsign_value(app, sess['_github_state_'])
                assert 'via' in state
                assert state['via'] == 'signup'


def test_signup_with_gitlab(app: Flask):
    with patch("authlib.flask.client.oauth.session", new={}) as sess:
        with app.app_context():
            with app.test_request_context('/auth/signup/with/gitlab'):
                resp = signup_with('gitlab')
                assert resp.status_code == 302
                p = urlparse(resp.location)
                q = parse_qs(p.query)
                assert q['response_type'] == ['code']
                assert q['client_id'] == ['None']
                assert q['scope'] == ['read_user']

                p = urlparse(q['redirect_uri'][0])
                assert p.path == '/auth/allowed/via/gitlab'

                assert '_gitlab_state_' in sess
                state = unsign_value(app, sess['_gitlab_state_'])
                assert 'via' in state
                assert state['via'] == 'signup'


def test_failing_if_missing_via_source(app: Flask):
    with app.app_context():
        signed_value = sign_value(app, {'via': 'signin'})
        path = '/auth/allowed/via/gitlab?state={}'.format(signed_value)
        with app.test_request_context('/auth/allowed/via/gitlab'):
            with pytest.raises(exceptions.BadRequest):
                authed('gitlab')


def test_failing_if_via_source_not_expected(app: Flask):
    with app.app_context():
        signed_value = sign_value(app, {'via': 'wherever'})
        path = '/auth/allowed/via/gitlab?state={}'.format(signed_value)
        with app.test_request_context('/auth/allowed/via/gitlab'):
            with pytest.raises(exceptions.BadRequest):
                authed('gitlab')


def test_failing_to_auth_if_with_unknown_provider(app: Flask):
    with app.app_context():
        signed_value = sign_value(app, {'via': 'signin'})
        path = '/auth/allowed/via/whatever?state={}'.format(signed_value)
        with app.test_request_context(path):
            with pytest.raises(exceptions.NotFound):
                authed('whatever')


def test_auth_redirect_when_missing_code_and_token(app: Flask):
    with app.app_context():
        signed_value = sign_value(app, {'via': 'signin'})
        path = '/auth/allowed/via/gitlab?state={}'.format(signed_value)
        with app.test_request_context(path):
            resp = authed('gitlab')
            assert resp.status_code == 302
            assert resp.location == "/"


def test_auth_redirect_to_signup_when_account_does_not_exist(app: Flask):
    func = "chaoshubdashboard.auth.views.get_user_profile_info_from_oauth"
    with patch(func) as gp:
        profile = ProfileInfo(
            sub="12345",
            name="Jane Doe"
        )
        gp.return_value = profile
        with patch("chaoshubdashboard.auth.views.get_account_by_subject") as get_acc:
            get_acc.return_value = None
            with patch("chaoshubdashboard.auth.session") as sess:
                with app.app_context():
                    signed_value = sign_value(app, {'via': 'signin'})
                    path = '/auth/allowed/via/google?state={}&id_token={}'\
                        .format(signed_value, 'myidtoken')
                    with app.test_request_context(path):
                        nonce = generate_nonce_key("google")
                        resp = authed('google')

                        assert resp.status_code == 302
                        assert resp.location == "/signup"


def test_auth_redirect_to_signin_when_account_already_exists(app: Flask):
    func = "chaoshubdashboard.auth.views.get_user_profile_info_from_oauth"
    with patch(func) as gp:
        profile = ProfileInfo(
            sub="12345",
            name="Jane Doe"
        )
        gp.return_value = profile

        with patch("chaoshubdashboard.auth.views.get_account_by_subject") as get_acc:
            account = Account.query.filter(
                Account.id=="c1337e77-ccaf-41cf-a68c-d6e2026aef21").first()
            get_acc.return_value = account
            with patch("chaoshubdashboard.auth.session") as sess:
                with app.app_context():
                    signed_value = sign_value(app, {'via': 'signup'})
                    path = '/auth/allowed/via/google?state={}&id_token={}'\
                        .format(signed_value, 'myidtoken')
                    with app.test_request_context(path):
                        nonce = generate_nonce_key("google")
                        resp = authed('google')

                        assert resp.status_code == 302
                        assert resp.location == "/signin"


def test_auth_redirect_to_home_on_signin(app: Flask):
    func = "chaoshubdashboard.auth.views.get_user_profile_info_from_oauth"
    with patch(func) as gp:
        profile = ProfileInfo(
            sub="12345",
            name="Jane Doe"
        )
        gp.return_value = profile
        with patch("chaoshubdashboard.auth.views.get_account_by_subject") as get_acc:
            account = Account.query.filter(
                Account.id=="c1337e77-ccaf-41cf-a68c-d6e2026aef21").first()
            get_acc.return_value = account
            with patch("chaoshubdashboard.auth.views.handle_signin") as hs:
                with patch("chaoshubdashboard.auth.session") as sess:
                    with app.app_context():
                        signed_value = sign_value(app, {'via': 'signin'})
                        path = '/auth/allowed/via/google?state={}&id_token={}'\
                            .format(signed_value, 'myidtoken')
                        with app.test_request_context(path):
                            nonce = generate_nonce_key("google")
                            resp = authed('google')

                            assert resp.status_code == 303
                            assert resp.location == "/"

                            hs.assert_called_with(
                                account, {'id_token': 'myidtoken'}, 'google')


def test_auth_redirect_to_home_on_signup(app: Flask):
    func = "chaoshubdashboard.auth.views.get_user_profile_info_from_oauth"
    with patch(func) as gp:
        profile = ProfileInfo(
            sub="12345",
            name="Jane Doe"
        )
        gp.return_value = profile
        with patch("chaoshubdashboard.auth.views.get_account_by_subject") as get_acc:
            get_acc.return_value = None
            with patch("chaoshubdashboard.auth.views.handle_signup") as hs:
                with patch("chaoshubdashboard.auth.session") as sess:
                    with app.app_context():
                        signed_value = sign_value(app, {'via': 'signup'})
                        path = '/auth/allowed/via/google?state={}&id_token={}'\
                            .format(signed_value, 'myidtoken')
                        with app.test_request_context(path):
                            nonce = generate_nonce_key("google")
                            resp = authed('google')

                            assert resp.status_code == 303
                            assert resp.location == "/"

                            hs.assert_called_with(
                                profile, {'id_token': 'myidtoken'}, 'google')
