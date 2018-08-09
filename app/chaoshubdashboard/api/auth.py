# -*- coding: utf-8 -*-
from typing import Any, Dict

from .model import db, APIAccessToken

__all__ = ["revoke_access_token", "set_access_token"]


def set_access_token(access_token: Dict[str, Any]):
    token = APIAccessToken.from_dict(access_token)
    db.session.add(token)
    db.session.commit()


def revoke_access_token(access_token: str):
    token = APIAccessToken.get_by_token(access_token)
    if token:
        token.revoke()
        db.session.add(token)
        db.session.commit()
