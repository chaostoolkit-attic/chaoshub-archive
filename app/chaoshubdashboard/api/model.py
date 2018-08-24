# -*- coding: utf-8 -*-
from datetime import datetime, timezone
import sys
from typing import Any, Dict, List, Optional, Union
import uuid

from authlib.flask.oauth2.sqla import OAuth2ClientMixin, OAuth2TokenMixin
from flask_sqlalchemy import SQLAlchemy as SA
import shortuuid
from sqlalchemy.sql import func
from sqlalchemy_json import NestedMutable
from sqlalchemy_utils import UUIDType
from sqlalchemy_utils import JSONType as JSONB

from chaoshubdashboard.model import db, get_user_info_secret_key

__all__ = ["db", "APIAccessToken"]


class APIAccessToken(db.Model):  # type: ignore
    __bind_key__ = 'api_service'
    __tablename__ = 'api_access_token'
    __table_args__ = (
        db.UniqueConstraint(
            'name', 'account_id', name='name_account_uniq'
        ),
    )

    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)
    account_id = db.Column(UUIDType(binary=False), nullable=False)
    last_used_on = db.Column(db.DateTime())
    client_id = db.Column(db.String(48))
    token_type = db.Column(db.String(40))
    access_token = db.Column(db.String(255), unique=True, nullable=False)
    refresh_token = db.Column(db.String(255), index=True)
    scope = db.Column(db.Text, default='')
    # be conservative
    revoked = db.Column(db.Boolean, nullable=False, default=True)
    issued_at = db.Column(db.Integer, nullable=False)
    expires_in = db.Column(db.Integer, nullable=False, default=0)

    def get_scope(self):
        return self.scope

    def get_expires_in(self):
        return self.expires_in

    def get_expires_at(self):
        return self.issued_at + self.expires_in

    def is_expired(self):
        now = datetime.utcnow().timestamp()
        return self.get_expires_at() < now

    def is_active(self):
        now = datetime.utcnow().timestamp()
        return self.get_expires_at() >= now

    def revoke(self):
        self.revoked = True

    def to_dict(self):
        last_used = None
        if self.last_used_on:
            last_used = self.last_used_on.replace(
                tzinfo=timezone.utc).timestamp()

        return {
            "id": str(self.id),
            "account_id": str(self.account_id),
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "scope": self.scope,
            "token_type": self.token_type,
            "issued_at": self.issued_at,
            "expires_in": self.expires_in,
            "last_used": last_used,
            "revoked": self.revoked
        }

    @staticmethod
    def from_dict(token: Dict[str, Any]) -> 'APIAccessToken':
        """
        Create or update a token from the source access token.

        On update, only the scope, revoked and dates properties are changed.
        Others are left as they are.
        """
        access_token = APIAccessToken.get_by_token(
            token["access_token"])
        if not access_token:
            access_token = APIAccessToken()
            access_token.id = shortuuid.decode(token["id"])
            access_token.account_id = shortuuid.decode(token["account_id"])
            access_token.access_token = token["access_token"]
            access_token.client_id = token["client_id"]

        access_token.name = token["name"]
        access_token.refresh_token = token["refresh_token"]
        access_token.scope = token["scope"]
        access_token.revoked = token["revoked"]
        access_token.issued_at = token["issued_at"]
        access_token.expires_in = token["expires_in"]

        return access_token

    @staticmethod
    def get_by_token(access_token: str) -> Optional['APIAccessToken']:
        return APIAccessToken.query.filter(
            APIAccessToken.access_token==access_token).first()

    @staticmethod
    def get_by_id_for_account(account_id: str,
                              token_id: str) -> Optional['APIAccessToken']:
        return APIAccessToken.query.filter(
            APIAccessToken.account_id==account_id,
            APIAccessToken.id==token_id).first()

    @staticmethod
    def get_all_for_account(account_id: str) -> List['APIAccessToken']:
        return APIAccessToken.query.filter(
            APIAccessToken.account_id==account_id).all()

    @staticmethod
    def get_active_for_account(account_id: str) -> List['APIAccessToken']:
        non_revoked_tokens = APIAccessToken.query.filter(
            APIAccessToken.revoked==False,
            APIAccessToken.account_id==account_id).all()

        return [token for token in non_revoked_tokens if token.is_active()]
