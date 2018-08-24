# -*- coding: utf-8 -*-
from typing import Any, Dict

__all__ = ["AccessToken", "Experiment", "ProfileInfo", "UserClaim",
           "Workspace"]


AccessToken = Dict[str, Any]
ProfileInfo = Dict[str, str]
UserClaim = Dict[str, Any]
Workspace = Dict[str, Any]
Experiment = Dict[str, Any]
Execution = Dict[str, Any]
