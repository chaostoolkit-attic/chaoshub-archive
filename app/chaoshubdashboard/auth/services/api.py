# -*- coding: utf-8 -*-
from ..types import UserClaim

from chaoshubdashboard.api.auth import set_access_token, \
    revoke_access_token as _revoke_access_token

from ..model import AccessToken

__all__ = ["revoke_access_token", "set_access_token"]


def create_access_token(access_token: AccessToken):
    """
    Broadcast an access token to the experiment service
    """
    token = access_token.to_dict()
    set_access_token(token)


def revoke_access_token(access_token: AccessToken):
    """
    Broadcast access token revocation to the experiment service
    """
    _revoke_access_token(access_token.access_token)
