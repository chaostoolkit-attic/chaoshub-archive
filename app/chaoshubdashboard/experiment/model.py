# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from enum import Enum, IntEnum
import sys
from typing import Any, Dict, List, Optional, Union
import uuid

import shortuuid
from sqlalchemy.sql import func
from sqlalchemy_json import NestedMutable
from sqlalchemy_utils import UUIDType
from sqlalchemy_utils import JSONType as JSONB

from chaoshubdashboard.model import db, get_user_info_secret_key

from .types import ScheduleContext

__all__ = ["db", "Discovery", "Event", "Experiment",
           "ExperimentSuggestion", "Init", "Execution", "Schedule"]


class Discovery(db.Model):  # type: ignore
    __bind_key__ = 'experiment_service'
    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUIDType(binary=False), nullable=False, index=True)
    received_date = db.Column(db.DateTime(), server_default=func.now())
    workspace_id = db.Column(
        UUIDType(binary=False), nullable=False, index=True)
    payload = db.Column(JSONB())


class Experiment(db.Model):  # type: ignore
    __bind_key__ = 'experiment_service'
    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    shared_ref = db.Column(UUIDType(binary=False), nullable=False, index=True)
    account_id = db.Column(UUIDType(binary=False), nullable=False, index=True)
    created_date = db.Column(db.DateTime(), server_default=func.now())
    updated_date = db.Column(
        db.DateTime(), server_default=func.now(), server_onupdate=func.now())
    suggested_experiment_id = db.Column(UUIDType(binary=False), index=True)
    org_id = db.Column(
        UUIDType(binary=False), nullable=False, index=True)
    workspace_id = db.Column(
        UUIDType(binary=False), nullable=False, index=True)
    executions = db.relationship(
        'Execution', backref='experiment', cascade="all, delete-orphan")
    payload = db.Column(NestedMutable.as_mutable(JSONB), nullable=False)

    def to_dict(self, with_payload: bool = True):
        updated_date = None
        timestamp = self.created_date.timestamp()
        if self.updated_date:
            updated_date = "{}Z".format(self.updated_date.isoformat())
            timestamp = self.updated_date.timestamp()

        d = {
            "id": shortuuid.encode(self.id),
            "ref": shortuuid.encode(self.shared_ref),
            "created_date": "{}Z".format(self.created_date.isoformat()),
            "updated_date": updated_date,
            "timestamp": timestamp,
            "org": shortuuid.encode(self.org_id),
            "workspace": shortuuid.encode(self.workspace_id),
            "title": self.payload.get("title"),
            "description": self.payload.get("description")
        }

        if with_payload:
            d["payload"] = self.payload

        return d

    def to_public_dict(self, with_payload: bool = True):
        updated_date = None
        timestamp = self.created_date.timestamp()
        if self.updated_date:
            updated_date = "{}Z".format(self.updated_date.isoformat())
            timestamp = self.updated_date.timestamp()

        d = {
            "id": shortuuid.encode(self.id),
            "ref": shortuuid.encode(self.shared_ref),
            "created_date": "{}Z".format(self.created_date.isoformat()),
            "updated_date": updated_date,
            "timestamp": timestamp,
            "org": shortuuid.encode(self.org_id),
            "workspace": shortuuid.encode(self.workspace_id),
            "title": self.payload.get("title"),
            "description": self.payload.get("description"),
            "tags": [tag for tag in self.payload.get("tags", [])]
        }

        if with_payload:
            d["payload"] = self.payload

        return d

    @staticmethod
    def get_by_id(exp_id: Union[str, uuid.UUID]) -> Optional['Experiment']:
        if not exp_id:
            return None

        if isinstance(exp_id, str):
            try:
                exp_id = shortuuid.decode(exp_id)
            except ValueError:
                return None

        return Experiment.query.filter(Experiment.id==exp_id).first()

    def get_execution(self, timestamp: int) -> Optional['Execution']:
        return Execution.query.filter(
            Execution.experiment_id==self.id,
            Execution.timestamp==timestamp).first()


class Init(db.Model):  # type: ignore
    __bind_key__ = 'experiment_service'
    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUIDType(binary=False), nullable=False, index=True)
    received_date = db.Column(db.DateTime(), server_default=func.now())
    workspace_id = db.Column(
        UUIDType(binary=False), nullable=False, index=True)
    payload = db.Column(JSONB())


class Execution(db.Model):  # type: ignore
    __bind_key__ = 'experiment_service'
    __table_args__ = (
        db.UniqueConstraint(
            'timestamp', 'experiment_id', name='index_per_experiment_uniq'
        ),
    )

    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUIDType(binary=False), nullable=False, index=True)
    timestamp = db.Column(
        db.BigInteger,
        default=lambda: int(datetime.utcnow().timestamp() * 1000))
    org_id = db.Column(UUIDType(binary=False), nullable=False, index=True)
    workspace_id = db.Column(
        UUIDType(binary=False), nullable=False, index=True)
    experiment_id = db.Column(
        UUIDType(binary=False), db.ForeignKey(
            'experiment.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String)
    payload = db.Column(JSONB())

    def to_dict(self, visibility: str = "status") -> Dict[str, Any]:
        result = {
            "id": shortuuid.encode(self.id),
            "timestamp": self.timestamp,
            "org": shortuuid.encode(self.org_id),
            "workspace": shortuuid.encode(self.workspace_id),
            "experiment": shortuuid.encode(self.experiment_id)
        }

        if visibility == "full":
            result["status"] = self.status
            result["result"] = self.payload
        elif visibility == "full":
            result["status"] = self.status
        return result


class RecommendationTagsAssoc(db.Model):  # type: ignore
    __bind_key__ = 'experiment_service'
    __tablename__ = "recommendation_tags_assoc"
    recommendation_id = db.Column(
        UUIDType, db.ForeignKey('recommendation.id'), primary_key=True)
    tag_id = db.Column(
        db.Integer, db.ForeignKey('recommendation_tag.id'), primary_key=True)


class Recommendation(db.Model):  # type: ignore
    __bind_key__ = 'experiment_service'
    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    recommendation_type = db.Column(db.String(), index=True)
    tags = db.relationship(
        'RecommendationTag', secondary="recommendation_tags_assoc",
        backref=db.backref('recommendations', lazy=True))
    checksum = db.Column(db.String(), nullable=False)
    last_updated = db.Column(db.DateTime())
    rating = db.Column(db.Float, default=3.0)
    meta = db.Column(JSONB())
    data = db.Column(JSONB(), nullable=False)

    def to_dict(self):
        data = self.data
        if self.recommendation_type == "experiment":
            data = data["hashed"]
        return {
            "id": str(self.id),
            "type": self.recommendation_type,
            "tags": [tag.value for tag in self.tags],
            "checksum": self.checksum,
            "last_updated": "{}Z".format(self.last_updated.isoformat()),
            "meta": self.meta,
            "data": data
        }


class RecommendationTag(db.Model):  # type: ignore
    __bind_key__ = 'experiment_service'
    __tablename__ = "recommendation_tag"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(), nullable=False, unique=True)


class ScheduleStatus(Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class Schedule(db.Model):  # type: ignore
    __bind_key__ = 'experiment_service'
    id = db.Column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(UUIDType(binary=False), nullable=False, index=True)
    scheduled = db.Column(db.DateTime(), nullable=False)
    status = db.Column(
        db.Enum(ScheduleStatus), nullable=False,
        default=ScheduleStatus.pending)
    org_id = db.Column(
        UUIDType(binary=False), nullable=False, index=True)
    workspace_id = db.Column(
        UUIDType(binary=False), nullable=False, index=True)
    experiment_id = db.Column(
        UUIDType(binary=False), nullable=False, index=True)
    token_id = db.Column(UUIDType(binary=False), nullable=False)
    definition = db.Column(JSONB())
    info = db.Column(JSONB())

    def to_dict(self):
        return {
            "id": shortuuid.encode(self.id),
            "account_id": shortuuid.encode(self.account_id),
            "org_id": shortuuid.encode(self.org_id),
            "workspace_id": shortuuid.encode(self.workspace_id),
            "experiment_id": shortuuid.encode(self.experiment_id),
            "token_id": shortuuid.encode(self.token_id),
            "scheduled": "{}Z".format(self.scheduled.isoformat()),
            "definition": self.definition,
            "info": self.info
        }
