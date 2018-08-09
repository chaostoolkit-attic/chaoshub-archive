# -*- coding: utf-8 -*-
from typing import Any, Dict, TypeVar

__all__ = ["AccessToken", "Experiment", "Extension", "UserClaim", "Workspace",
           "Run", "Scheduler", "ScheduleContext", "ScheduleInfo", "Activity",
           "UserAccount", "Execution"]


AccessToken = Dict[str, Any]
UserClaim = Dict[str, Any]
Org = Dict[str, Any]
Workspace = Dict[str, Any]
Experiment = Dict[str, Any]
Extension = Dict[str, Any]
Execution = Dict[str, Any]
Run = Dict[str, Any]
ScheduleContext = Dict[str, Any]
ScheduleInfo = Dict[str, Any]
Scheduler = Any
Activity = Dict[str, Any]
UserAccount = Dict[str, Any]
