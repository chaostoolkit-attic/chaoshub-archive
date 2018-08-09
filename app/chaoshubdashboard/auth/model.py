# -*- coding: utf-8 -*-
from datetime import datetime
import sys
import uuid

from authlib.flask.oauth2.sqla import OAuth2ClientMixin, OAuth2TokenMixin
from flask_sqlalchemy import SQLAlchemy as SA
import shortuuid
from sqlalchemy.sql import func
from sqlalchemy_utils import PasswordType, UUIDType
from sqlalchemy_utils import JSONType as JSONB

from chaoshubdashboard.model import db, get_user_info_secret_key

__all__ = ["Client", "AccessToken", "Account", "ProviderToken", "LocalAccount"]


class Account(db.Model):  # type: ignore
    __bind_key__ = 'auth_service'
    __table_args__ = (
        db.UniqueConstraint(
            'oauth_provider', 'oauth_provider_sub',
            name='oauth_provider_sub_uniq'
        ),
    )

    id = db.Column(
        UUIDType(binary=False), primary_key=True, unique=True,
        default=uuid.uuid4)
    joined_on = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_since = db.Column(db.DateTime(timezone=True), nullable=True)
    inactive_since = db.Column(db.DateTime(timezone=True), nullable=True)
    is_closed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    oauth_provider = db.Column(db.String, nullable=True)
    oauth_provider_sub = db.Column(db.String, nullable=True)

    access_tokens = db.relationship(
        'AccessToken', backref='account', cascade="all, delete-orphan")
    client = db.relationship(
        'Client', backref='account', uselist=False,
        cascade="all, delete-orphan")
    local = db.relationship(
        'LocalAccount', backref='account', uselist=False,
        cascade="all, delete-orphan")

    def to_dict(self):
        inactive = closed = None
        if self.inactive_since:
            inactive = "{}Z".format(self.inactive_since.isoformat())
        if self.closed_since:
            closed = "{}Z".format(self.closed_since.isoformat())

        return {
            "id": str(self.id),
            "short_id": shortuuid.encode(self.id),
            "closed": self.is_closed,
            "active": self.is_active,
            "joined_on": "{}Z".format(self.joined_on.isoformat()),
            "inactive_since": inactive,
            "closed_since": closed,
            "client": self.client.to_dict() if self.client else None,
            "tokens": [t.to_dict() for t in self.access_tokens]
        }
    
    def turn_inactive(self):
        self.is_active = False
        self.inactive_since = datetime.utcnow()

    def turn_active(self):
        self.is_active = True
        self.inactive_since = None

    def close_account(self):
        self.is_closed = False
        self.closed_since = datetime.utcnow()


class Client(db.Model, OAuth2ClientMixin):  # type: ignore
    __bind_key__ = 'auth_service'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(
        UUIDType(binary=False), db.ForeignKey(
            'account.id', ondelete='CASCADE'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }


class AccessToken(db.Model, OAuth2TokenMixin):  # type: ignore
    __bind_key__ = 'auth_service'
    id = db.Column(
        UUIDType(binary=False), primary_key=True, unique=True,
        default=uuid.uuid4)
    name = db.Column(db.String(), nullable=False)
    account_id = db.Column(
        UUIDType(binary=False), db.ForeignKey(
            'account.id', ondelete='CASCADE'), nullable=False)
    last_used_on = db.Column(db.DateTime())

    def to_dict(self):
        last_used = None
        if self.last_used_on:
            last_used = "{}Z".format(self.last_used_on.isoformat())

        return {
            "id": shortuuid.encode(self.id),
            "name": self.name,
            "account_id": shortuuid.encode(self.account_id),
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


class ProviderToken(db.Model, OAuth2TokenMixin):  # type: ignore
    __bind_key__ = 'auth_service'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    account_id = db.Column(
        UUIDType(binary=False), db.ForeignKey(
            'account.id', ondelete='CASCADE'))
    account = db.relationship('Account')

    def to_dict(self):
        return {
            "id": self.id,
            "access_token": self.access_token,
            "token_type": self.token_type,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_in,
            "revoked": self.revoked
        }


class LocalAccount(db.Model):  # type: ignore
    __bind_key__ = 'auth_service'

    id = db.Column(
        UUIDType(binary=False), primary_key=True, unique=True,
        default=uuid.uuid4)
    account_id = db.Column(
        UUIDType(binary=False), db.ForeignKey(
            'account.id', ondelete='CASCADE'), nullable=False)
    username = db.Column(db.String, nullable=False, unique=True, index=True)
    password = db.Column(
        PasswordType(
            schemes=['pbkdf2_sha512'],
        ),
        unique=False,
        nullable=False)
