# -*- coding: utf-8 -*-
from typing import List, Optional

from chaoshubdashboard.auth import get_active_access_tokens, get_access_token

from ..types import AccessToken, UserClaim


__all__ = ["get_user_access_tokens"]


def get_user_access_tokens(user_claim: UserClaim) -> List[AccessToken]:
    return get_active_access_tokens(user_claim)


def get_user_access_token(user_claim: UserClaim,
                          token_id: str) -> Optional[AccessToken]:
    return get_access_token(user_claim, token_id)
