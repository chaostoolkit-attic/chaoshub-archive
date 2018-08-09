# -*- coding: utf-8 -*-
from authlib.specs.oidc import UserInfo as ProfileInfo

from ..types import UserClaim

from chaoshubdashboard.dashboard import register_user

__all__ = ["register_new_user"]


def register_new_user(user_claim: UserClaim, profile: ProfileInfo):
    """
    Register a new user with the dashboard service.
    """
    register_user(user_claim, profile)
