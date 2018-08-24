# -*- coding: utf-8 -*-
from flask import Flask

from chaoshubdashboard.auth import generate_access_token, revoke_access_token
from ..types import AccessToken, UserClaim

__all__ = ["new_access_token", "revoke_user_access_token"]


def new_access_token(user_claim: UserClaim, token_name: str) -> AccessToken:
    """
    Generate a new access token for that user.
    """
    token = generate_access_token(user_claim, token_name)
    return token


def revoke_user_access_token(user_claim: UserClaim, token_id: str):
    """
    Revoke the given access token of that user.
    """
    revoke_access_token(user_claim["id"], token_id)
