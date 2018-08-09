# -*- coding: utf-8 -*-
from typing import List, Optional

from chaoshubdashboard.dashboard import get_workspace, record_activity

from ..types import Activity, UserClaim, Workspace

__all__ = ["get_context"]


def get_context(user_claim: UserClaim, org: str,
                workspace: str) -> Optional[Workspace]:
    """
    Retrieve the org/workspace context for from their names for the given
    user account.
    """
    return get_workspace(user_claim, org, workspace)


def push_activity(activity: Activity):
    record_activity(activity)
