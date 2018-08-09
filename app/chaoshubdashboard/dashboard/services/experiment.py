# -*- coding: utf-8 -*-
from typing import List, Optional, Union
import uuid

import shortuuid

from chaoshubdashboard.experiment import get_last_updated_experiments, \
    get_recent_experiments_in_org, get_recent_experiments_in_workspace, \
    get_recent_public_experiments_in_org, get_experiment, \
    get_recent_executions_in_workspace, get_recent_executions_in_org

from ..model import Workspace
from ..types import Experiment, Execution, UserClaim

__all__ = ["get_user_last_experiments", "get_org_last_experiments",
           "get_workspace_last_experiments", "get_org_last_public_experiments",
           "get_workspace_last_public_experiments", "get_single_experiment",
           "get_workspace_last_executions", "get_org_last_executions"]


def get_single_experiment(experiment_id: str) -> Optional[Experiment]:
    """
    Retrieve the last updated experiments.
    """
    return get_experiment(experiment_id)


def get_user_last_experiments(user_claim: UserClaim) -> List[Experiment]:
    """
    Retrieve the last updated experiments.
    """
    experiments = get_last_updated_experiments(user_claim)
    for e in experiments:
        w = Workspace.query.filter(
            Workspace.id==shortuuid.decode(e["workspace"])).first()
        e["workspace"] = w.to_dict()
    return experiments


def get_workspace_last_experiments(workspace_id: str) -> List[Experiment]:
    """
    Retrieve the last updated experiments in a workspace.
    """
    experiments = get_recent_experiments_in_workspace(workspace_id)
    return experiments


def get_org_last_experiments(org_id: str) -> List[Experiment]:
    """
    Retrieve the last updated experiments in an organization.
    """
    experiments = get_recent_experiments_in_org(org_id)
    return experiments


def get_org_last_public_experiments(org_id: str,
                                    workspaces: List[str]) \
                                    -> List[Experiment]:
    """
    Retrieve the last updated public experiments in an organization.
    """
    experiments = get_recent_public_experiments_in_org(org_id, workspaces)
    return experiments


def get_org_last_executions(org_id: str, visibility: str = "status") \
                            -> List[Execution]:
    """
    Retrieve the last executions in an organization.
    """
    executions = get_recent_executions_in_org(org_id, visibility=visibility)
    return executions


def get_workspace_last_executions(workspace_id: str,
                                  visibility: str = "status") \
                                  -> List[Execution]:
    """
    Retrieve the last executions in a workspace.
    """
    executions = get_recent_executions_in_workspace(
        workspace_id, visibility=visibility)
    return executions
