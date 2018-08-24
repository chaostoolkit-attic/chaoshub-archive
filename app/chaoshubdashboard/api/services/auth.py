# -*- coding: utf-8 -*-
from flask import Flask

from chaoshubdashboard.auth import update_access_token
from ..types import AccessToken, UserClaim

__all__ = ["updated_user_access_token"]


def updated_user_access_token(token: AccessToken):
    update_access_token(token)
