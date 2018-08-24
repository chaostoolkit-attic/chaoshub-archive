# -*- coding: utf-8 -*-
from datetime import datetime
from enum import Enum, IntEnum, auto
import secrets
import sys
from typing import Any, Dict, List, Optional, Union
import uuid

from authlib.flask.oauth2.sqla import OAuth2ClientMixin, OAuth2TokenMixin
from flask_sqlalchemy import SQLAlchemy as SA
import shortuuid
import simplejson as json
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_json import NestedMutable
from sqlalchemy_utils import EmailType, EncryptedType, JSONType, UUIDType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from sqlalchemy_utils import JSONType as JSONB

from chaoshubdashboard.model import db, get_user_info_secret_key


__all__ = ["UserAccount", "AccountType", "OrgsMembers", "Activity",
           "WorkpacesMembers", "Company", "Privacy", "Org", "UserInfo",
           "WorkspaceType", "ExperimentVisibility", "OrgType",
           "ExperimentVisibility", "ActivityVisibility"]


class WorkpacesMembers(db.Model):  # type: ignore
    __bind_key__ = 'dashboard_service'
    __tablename__ = "workspaces_members"
    workspace_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('workspace.id'),
        primary_key=True)
    account_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('user_account.id'),
        primary_key=True)
    is_owner = db.Column(db.Boolean(), default=False)
    account = db.relationship('UserAccount')
    workspace = db.relationship('Workspace')


class OrgsMembers(db.Model):  # type: ignore
    __bind_key__ = 'dashboard_service'
    __tablename__ = "orgs_members"
    org_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('org.id'), primary_key=True)
    account_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('user_account.id'),
        primary_key=True)
    is_owner = db.Column(db.Boolean(), default=False)
    account = db.relationship('UserAccount')
    organization = db.relationship('Org')


class UserAccount(db.Model):  # type: ignore
    __bind_key__ = 'dashboard_service'
    __tablename__ = 'user_account'
    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    joined_dt = db.Column(db.DateTime(), server_default=func.now())
    closed_dt = db.Column(db.DateTime())
    inactive_dt = db.Column(db.DateTime())
    is_closed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    info = db.relationship(
        'UserInfo', backref='account', uselist=False,
        cascade="all, delete-orphan")
    privacy = db.relationship(
        'UserPrivacy', backref='account', uselist=False,
        cascade="all, delete-orphan")
    workspaces = db.relationship(
        'Workspace', secondary="workspaces_members",
        lazy='subquery', backref=db.backref('accounts', lazy=True))
    orgs = db.relationship(
        'Org', secondary="orgs_members", lazy='subquery',
        backref=db.backref('accounts', lazy=True))
    # direct access to the unique personal org
    # but this org is also part of the many to many relationship
    personal_org = db.relationship(
        'Org', backref='account', uselist=False, cascade="all, delete-orphan")

    def to_public_dict(self):
        return {
            "id": shortuuid.encode(self.id),
            "joined": "{}Z".format(self.joined_dt.isoformat()),
            "workspaces": [
                w.to_dict() for w in self.workspaces
            ],
            "orgs": [o.to_dict() for o in self.orgs]
        }

    def to_short_dict(self):
        return {
            "id": shortuuid.encode(self.id),
            "joined": "{}Z".format(self.joined_dt.isoformat()),
            "org": {
                "name": self.personal_org.name
            },
            "profile": self.info.to_public_dict()
        }


class UserInfo(db.Model):  # type: ignore
    __bind_key__ = 'dashboard_service'
    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('user_account.id'),
        nullable=False)
    last_updated = db.Column(
        db.DateTime(), server_default=func.now(),
        onupdate=func.current_timestamp())
    verified_email = db.Column(db.Boolean(), default=False)

    # values for search purpose mostly
    username = db.Column(db.String, index=True, nullable=True)
    fullname = db.Column(db.String, index=True, nullable=True)

    details = db.Column(
        EncryptedType(
            db.String, get_user_info_secret_key, AesEngine, 'pkcs5'),
        nullable=False)

    @staticmethod
    def get_for_account(account_id: Union[str, uuid.UUID]) -> 'UserInfo':
        """
        Lookup user info for the given user account
        """
        return UserInfo.query.filter(UserInfo.account_id==account_id).first()

    @property
    def profile(self) -> Dict[str, Any]:
        """
        The user's profile
        """
        return json.loads(self.details)

    @profile.setter
    def profile(self, p: Dict[str, Any]):
        """
        Set the user's profile from the given payload

        The payload is serialized to JSON and stored in the `details`
        property
        """
        self.details = json.dumps(p)

    def to_dict(self):
        return {
            "id": shortuuid.encode(self.id),
            "account": shortuuid.encode(self.account.id),
            "profile": self.profile
        }

    def to_public_dict(self):
        p = self.profile

        return {
            "id": shortuuid.encode(self.id),
            "username": p.get("preferred_username"),
            "name": p.get("name"),
            "picture": p.get("picture")
        }


class UserPrivacy(db.Model):  # type: ignore
    __bind_key__ = 'dashboard_service'
    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('user_account.id'),
        nullable=False)
    last_changed = db.Column(db.DateTime(), server_default=func.now())
    details = db.Column(JSONB())


class WorkspaceType(Enum):
    personal = "personal"
    protected = "protected"
    public = "public"


class ExperimentVisibility(Enum):
    private = "private"
    protected = "protected"
    public = "public"


class ExecutionVisibility(Enum):
    none = "none"
    status = "status"
    full = "full"


DEFAULT_WORKSPACE_SETTINGS = {
    "visibility": {
        "execution": {
            "anonymous": ExecutionVisibility.none.value,
            "members": ExecutionVisibility.full.value
        },
        "experiment": {
            "anonymous": ExperimentVisibility.public.value,
            "members": ExperimentVisibility.public.value,
        }
    }
}


class Workspace(db.Model):  # type: ignore
    __bind_key__ = 'dashboard_service'
    __table_args__ = (
        db.UniqueConstraint(
            'name', 'org_id', name='workspace_org_uniq'
        ),
    )

    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(), nullable=False)
    name_lower = db.Column(db.String(), nullable=False)
    kind = db.Column(
        db.Enum(WorkspaceType), nullable=False, default=WorkspaceType.personal)
    org_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('org.id'), nullable=False)
    settings = db.Column(
        JSONB(), nullable=False, default=DEFAULT_WORKSPACE_SETTINGS)

    def to_dict(self):
        return {
            "id": shortuuid.encode(self.id),
            "name": self.name,
            "type": self.kind.value,
            "org": {
                "id": shortuuid.encode(self.org_id),
                "name": self.org.name,
                "type": self.org.kind.value
            },
            "settings": self.settings
        }

    def to_short_dict(self):
        return {
            "id": shortuuid.encode(self.id),
            "name": self.name,
            "type": self.kind.value,
            "settings": self.settings
        }

    @staticmethod
    def find_by_name(workspace_name: str) -> 'Workspace':
        """
        Get a workspace by its name
        """
        return Workspace.query.filter(
            Workspace.name_lower==workspace_name.lower()).first()

    @staticmethod
    def get_by_id(workspace_id: Union[str, uuid.UUID]) -> 'Workspace':
        """
        Get a workspace by its identifier
        """
        return Workspace.query.filter(Workspace.id==workspace_id).first()

    def is_collaborator(self, account_id: Union[str, uuid.UUID]) -> bool:
        """
        Return `True` when the given account is a collaborator to this
        workspace
        """
        return WorkpacesMembers.query.filter(
            WorkpacesMembers.workspace_id==self.id,
            WorkpacesMembers.account_id==account_id).first() is not None

    def is_owner(self, account_id: Union[str, uuid.UUID]) -> bool:
        """
        Return `True` when the given account is an owner of the workspace
        """
        return WorkpacesMembers.query.filter(
            WorkpacesMembers.workspace_id==self.id,
            WorkpacesMembers.is_owner==True,
            WorkpacesMembers.account_id==account_id).first() is not None

    def has_single_owner(self) -> bool:
        """
        Return `True` if only one owner exists for this workspace
        """
        return WorkpacesMembers.query.filter(
            WorkpacesMembers.workspace_id==self.id,
            WorkpacesMembers.is_owner==True).count() == 1

    def make_collaborator(self, account_id: Union[str, uuid.UUID]):
        """
        Turn an user as a collaborator only of this workspace.
        """
        membership = WorkpacesMembers.query.filter(
            WorkpacesMembers.workspace_id==self.id,
            WorkpacesMembers.account_id==account_id).first()
        if membership:
            membership.is_owner = False

    def make_owner(self, account_id: Union[str, uuid.UUID]):
        """
        Turn an user as an owner of this workspace.
        """
        membership = WorkpacesMembers.query.filter(
            WorkpacesMembers.workspace_id==self.id,
            WorkpacesMembers.account_id==account_id).first()
        if membership:
            membership.is_owner = True

    def add_collaborator(self, account_id: Union[str, uuid.UUID]) \
            -> WorkpacesMembers:
        """
        Add this user to the organization as a collaborator
        """
        membership = WorkpacesMembers(
            workspace_id=self.id, account_id=account_id)
        db.session.add(membership)
        return membership

    def remove_collaborator(self, account_id: Union[str, uuid.UUID]):
        """
        Remove this collaborator from the organization
        """
        WorkpacesMembers.query.filter(
            WorkpacesMembers.workspace_id==self.id,
            WorkpacesMembers.account_id==account_id).delete()


class OrgType(Enum):
    personal = "personal"
    collaborative = "collaborative"


DEFAULT_ORG_SETTINGS = {  # type: ignore
    "meta": {},
    "visibility": {
        "execution": {
            "anonymous": ExecutionVisibility.none.value,
            "members": ExecutionVisibility.full.value
        },
        "experiment": {
            "anonymous": ExperimentVisibility.public.value,
            "members": ExperimentVisibility.public.value,
        }
    }
}


class Org(db.Model):  # type: ignore
    __bind_key__ = 'dashboard_service'

    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    # only set when this is a personal org linked to a single account,
    # otherwise it's not set
    account_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('user_account.id'),
        nullable=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    name_lower = db.Column(db.String(), nullable=False, unique=True)
    kind = db.Column(
        db.Enum(OrgType), nullable=False, default=OrgType.personal)
    created_on = db.Column(db.DateTime(), server_default=func.now())
    workspaces = db.relationship(
        'Workspace', backref='org', cascade="all, delete-orphan")
    settings = db.Column(
        JSONB(), nullable=False, default=DEFAULT_ORG_SETTINGS)

    def to_dict(self, public_workspaces_only: bool = False):
        workspaces = []
        for w in self.workspaces:
            if public_workspaces_only and w.kind != WorkspaceType.public:
                continue

            workspaces.append({
                "id": shortuuid.encode(w.id),
                "name": w.name
            })

        return {
            "id": shortuuid.encode(self.id),
            "name": self.name,
            "settings": self.settings,
            "type": self.kind.value,
            "created_on": "{}Z".format(self.created_on.isoformat()),
            "workspaces": workspaces
        }

    def to_short_dict(self):
        return {
            "id": shortuuid.encode(self.id),
            "name": self.name,
            "created_on": "{}Z".format(self.created_on.isoformat()),
            "settings": self.settings,
            "type": self.kind.value
        }

    @staticmethod
    def get_next_available_name(suggested_name: str) -> str:
        """
        Return the next available name prefixed by the given suggested name and
        suffixed by a number between 0 and 1000.

        If `suggested_name` is not used yet, return it as the available name
        """
        while True:
            has_org = Org.query.filter(Org.name==suggested_name).first()
            if not has_org:
                return suggested_name
            suggested_name = "{}{}".format(
                suggested_name, secrets.randbelow(1000))

    @staticmethod
    def get_by_id(org_id: Union[str, uuid.UUID]) -> 'Org':
        """
        Lookup an organization by its identifier
        """
        return Org.query.filter(Org.id==org_id).first()

    @staticmethod
    def find_by_name(org_name: str) -> 'Org':
        """
        Lookup an organization by its name
        """
        return Org.query.filter(Org.name_lower==org_name.lower()).first()

    def find_workspace_by_name(self,
                               workspace_name: str) -> Optional[Workspace]:
        """
        Lookup a workspace in the organization by its name
        """
        w_name = workspace_name.lower()
        for workspace in self.workspaces:
            if workspace.name_lower == w_name:
                return workspace

        return None

    def is_member(self, account_id: Union[str, uuid.UUID]) -> bool:
        """
        Return `True` when the given account is a member of the organization
        """
        return OrgsMembers.query.filter(
            OrgsMembers.org_id==self.id,
            OrgsMembers.account_id==account_id).first() is not None

    def is_owner(self, account_id: Union[str, uuid.UUID]) -> bool:
        """
        Return `True` when the given account is an owner of the organization
        """
        return OrgsMembers.query.filter(
            OrgsMembers.org_id==self.id, OrgsMembers.is_owner==True,
            OrgsMembers.account_id==account_id).first() is not None

    def has_single_owner(self) -> bool:
        """
        Return `True` if only one owner exists for this organization
        """
        return OrgsMembers.query.filter(
            OrgsMembers.org_id==self.id,
            OrgsMembers.is_owner==True).count() == 1

    def make_member(self, account_id: Union[str, uuid.UUID]):
        """
        Turn an user as a member only of this organization.

        The user must already be part of this organization, this is mostly
        therefore useful when moving an owner down to simple member.
        """
        membership = OrgsMembers.query.filter(
            OrgsMembers.org_id==self.id,
            OrgsMembers.account_id==account_id).first()
        if membership:
            membership.is_owner = False

    def make_owner(self, account_id: Union[str, uuid.UUID]):
        """
        Turn an user as an owner of this organization.
        """
        membership = OrgsMembers.query.filter(
            OrgsMembers.org_id==self.id,
            OrgsMembers.account_id==account_id).first()
        if membership:
            membership.is_owner = True

    def add_member(self, account_id: Union[str, uuid.UUID]) -> OrgsMembers:
        """
        Add this user to the organization as a member
        """
        membership = OrgsMembers(org_id=self.id, account_id=account_id)
        db.session.add(membership)
        return membership

    def remove_member(self, account_id: Union[str, uuid.UUID]):
        """
        Remove this member from the organization
        """
        OrgsMembers.query.filter(
            OrgsMembers.org_id==self.id,
            OrgsMembers.account_id==account_id).delete()

    def get_public_workspace_ids(self) -> List[uuid.UUID]:
        """
        List all public workspaces in this organization and return their
        identifiers
        """
        result = db.session.query(Workspace.id).filter(
            Workspace.org_id==self.id,
            Workspace.kind==WorkspaceType.public).all()
        if not result:
            return []

        return result[0]


class ActivityVisibility(IntEnum):
    anonymous = 1
    authenticated = 2
    collaborator = 3
    owner = 4


class Activity(db.Model):  # type: ignore
    __bind_key__ = 'dashboard_service'

    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUIDType(binary=False), nullable=True)
    org_id = db.Column(UUIDType(binary=False), nullable=True)
    workspace_id = db.Column(UUIDType(binary=False), nullable=True)
    experiment_id = db.Column(UUIDType(binary=False), nullable=True)
    execution_id = db.Column(UUIDType(binary=False), nullable=True)
    timestamp = db.Column(
        db.BigInteger,
        default=lambda: int(datetime.utcnow().timestamp() * 1000))
    kind = db.Column(db.String, nullable=True)
    visibility = db.Column(
        db.Enum(ActivityVisibility), nullable=False,
        default=ActivityVisibility.authenticated)
    title = db.Column(db.String, nullable=False)
    info = db.Column(db.String, nullable=True)
    extra = db.Column(JSONB(), nullable=True)

    def to_dict(self):
        org_id = shortuuid.encode(self.org_id) if self.org_id else None
        workspace_id = None
        if self.workspace_id:
            workspace_id = shortuuid.encode(self.workspace_id)
        experiment_id = None
        if self.experiment_id:
            experiment_id = shortuuid.encode(self.experiment_id)
        execution_id = None
        if self.execution_id:
            execution_id = shortuuid.encode(self.execution_id)

        return {
            "id": shortuuid.encode(self.id),
            "account_id": shortuuid.encode(self.account_id),
            "workspace_id": workspace_id,
            "org_id": org_id,
            "experiment_id": experiment_id,
            "execution_id": execution_id,
            "type": self.kind,
            "visibility": self.visibility.value,
            "timestamp": self.timestamp,
            "title": self.title,
            "info": self.info,
            "extra": self.extra
        }

    @staticmethod
    def from_dict(activity: Dict[str, Any]) -> 'Activity':
        visibility = activity["visibility"]
        if visibility in (1, "anonymous"):
            visibility = ActivityVisibility.anonymous
        elif visibility in (2, "authenticated"):
            visibility = ActivityVisibility.authenticated
        elif visibility in (3, "collaborator"):
            visibility = ActivityVisibility.collaborator
        elif visibility in (4, "owner"):
            visibility = ActivityVisibility.owner

        org_id = activity.get("org_id")
        if org_id:
            org_id = shortuuid.decode(org_id)

        workspace_id = activity.get("workspace_id")
        if workspace_id:
            workspace_id = shortuuid.decode(workspace_id)

        experiment_id = activity.get("experiment_id")
        if experiment_id:
            experiment_id = shortuuid.decode(experiment_id)

        execution_id = activity.get("execution_id")
        if execution_id:
            execution_id = shortuuid.decode(execution_id)

        return Activity(
            account_id=shortuuid.decode(activity.get("account_id")),
            org_id=org_id,
            workspace_id=workspace_id,
            experiment_id=experiment_id,
            execution_id=execution_id,
            kind=activity.get("type"),
            visibility=visibility,
            title=activity.get("title"),
            info=activity.get("info"),
            extra=activity.get("extra"),
            timestamp=activity.get("timestamp")
        )

    @staticmethod
    def get_recents_for_account(account_id: Union[str, uuid.UUID],
                                visibility: ActivityVisibility,
                                last: int = 10) -> List['Activity']:
        return Activity.query.filter(
            Activity.account_id==account_id,
            Activity.visibility<=visibility)\
            .order_by(Activity.timestamp.desc())\
            .limit(last)

    @staticmethod
    def get_recents_for_org(org_id: Union[str, uuid.UUID],
                            visibility: ActivityVisibility,
                            last: int = 10) -> List['Activity']:
        return Activity.query.filter(
            Activity.org_id==org_id,
            Activity.visibility<=visibility)\
            .order_by(Activity.timestamp.desc())\
            .limit(last)

    @staticmethod
    def get_recents_for_workspace(workspace_id: Union[str, uuid.UUID],
                                  visibility: ActivityVisibility,
                                  last: int = 10) -> List['Activity']:
        return Activity.query.filter(
            Activity.workspace_id==workspace_id,
            Activity.visibility<=visibility)\
            .order_by(Activity.timestamp.desc())\
            .limit(last)
