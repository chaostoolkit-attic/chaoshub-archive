# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional

from ..types import UserClaim, Execution, Experiment, Workspace

from chaoshubdashboard.experiment import \
    get_experiment_in_workspace_for_user, store_experiment, store_execution

__all__ = ["get_experiment"]


def get_experiment(user_claim: UserClaim, org: str,
                   workspace: str, experiment_id: str) -> Optional[Workspace]:
    """
    Retrieve the org/workspace context for from their names for the given
    user account.
    """
    return get_experiment_in_workspace_for_user(
        user_claim, org, workspace, experiment_id, include_payload=True)


def create_experiment(user_claim: UserClaim, org: str,
                      workspace: str, payload: Dict[str, Any]) -> Experiment:
    return store_experiment(user_claim, org, workspace, payload)


def create_execution(user_claim: UserClaim, org: str,
                     workspace: str, experiment: str,
                     payload: Dict[str, Any]) -> Execution:
    return store_execution(user_claim, org, workspace, experiment, payload)
