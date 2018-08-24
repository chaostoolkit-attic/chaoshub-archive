# -*- coding: utf-8 -*-
from datetime import datetime
import os
from typing import Callable, Dict, List
from unittest.mock import MagicMock, patch

from authlib.specs.oidc import UserInfo as ProfileInfo
import dateparser
from flask import Flask
import pytest
import simplejson as json

from chaoshubdashboard.app import create_app
from chaoshubdashboard.model import db
from chaoshubdashboard.dashboard import create_user_account, set_user_profile, \
    set_user_privacy, add_default_org_to_account, \
    add_private_workspace_to_account, add_public_workspace_to_account
from chaoshubdashboard.dashboard.model import UserPrivacy, UserAccount, \
   UserInfo, WorkpacesMembers, Workspace, WorkspaceType
from chaoshubdashboard.settings import load_settings


@pytest.fixture(scope="session")
def app() -> Flask:
    load_settings(os.path.join(os.path.dirname(__file__), "..", ".env.test"))
    application = create_app()

    with application.app_context():
        db.create_all(bind='dashboard_service')
    
    return application


@pytest.fixture(scope="session", autouse=True)
def default_dataset(app: Flask):
    with app.app_context():
        profile_info = ProfileInfo(
            sub="12345",
            preferred_username="TheDude",
            email="the@dude.com",
            name="Jon Doe"
        )

        claim = {
            "id": "c1337e77-ccaf-41cf-a68c-d6e2026aef21"
        }

        account = create_user_account(claim)
        profile = set_user_profile(account, profile_info)
        privacy = set_user_privacy(account)
        org = add_default_org_to_account(account, "TheDude")
        personal_workspace = add_private_workspace_to_account(account, org)
        public_workspace = add_public_workspace_to_account(account, org)

        profile.id = "9c5c0aff-4cd2-482c-a25b-7611d6f4496a"
        profile.last_updated=dateparser.parse("2018-04-01T18:12:48.681677Z")
        profile.details = json.dumps(profile_info)

        privacy.id = "d9b8def4-04de-4de1-837c-329f59c63b6f"

        account.id = "c1337e77-ccaf-41cf-a68c-d6e2026aef21"
        account.joined_dt =dateparser.parse("2018-04-01T18:11:48.681677Z")

        personal_workspace.id = "b393802e-182d-464f-9747-1a642953fd1d"
        public_workspace.id = "08faab84-2302-4f89-bc85-444bd43d1195"

        db.session.commit()
