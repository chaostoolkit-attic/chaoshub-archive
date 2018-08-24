# -*- coding: utf-8 -*-
from typing import List, Optional

from chaoshubdashboard.dashboard import get_workspace, get_workspace_by_id, \
    get_workspaces, record_activity, get_caller_info

from ..types import Activity, UserAccount, UserClaim, Workspace


__all__ = ["get_user_workspaces", "get_user_workspace", "get_user_details",
           "get_experiment_workspace", "push_activity"]


def get_user_details(user_claim: UserClaim, org_id: str,
                     workspace_id: str) -> Optional[UserAccount]:
    return get_caller_info(user_claim, org_id, workspace_id)


def get_user_workspaces(user_claim: UserClaim) -> List[Workspace]:
    """
    Retrieve the user's workspaces.
    """
    return get_workspaces(user_claim)


def get_user_workspace(user_claim: UserClaim, org_name: str,
                       workspace_name: str) -> Optional[Workspace]:
    """
    Retrieve a workspace.
    """
    return get_workspace(user_claim, org_name, workspace_name)


def get_experiment_workspace(user_claim: UserClaim,
                             workspace_id: str) -> Optional[Workspace]:
    """
    Retrieve a workspace by its id.
    """
    return get_workspace_by_id(user_claim, workspace_id)


def push_activity(activity: Activity):
    record_activity(activity)
