# -*- coding: utf-8 -*-
from typing import Any, Dict, List

import pkg_resources

from ..types import Scheduler, ScheduleContext

__all__ = ["register_schedulers", "schedule", "schedulers",
           "shutdown_schedulers", "is_scheduler_registered"]

# once this has been set, this shouldn't change so making it global is fair
_schedulers: Dict[str, Scheduler] = {}


def schedule(scheduler: str, context: ScheduleContext) -> str:
    """
    Schedule the given experiment execution context with the provided
    scheduler.
    """
    if scheduler not in _schedulers:
        raise KeyError("Invalid scheduler '{}'".format(scheduler))

    sched = _schedulers[scheduler]
    return sched.schedule(context)


def register_schedulers(config: Dict[str, Any]) -> Dict[str, Scheduler]:
    """
    Register all the installed experiment schedulers
    """
    _schedulers.clear()
    for entry_point in pkg_resources.iter_entry_points('chaoshub.scheduling'):
        klass = entry_point.load()

        current_configs = {
            k.replace(klass.settings_key_prefix, "").lower(): v
            for (k, v) in config.items()
            if k.startswith(klass.settings_key_prefix)
        }
        _schedulers[klass.name] = klass(**current_configs)

    return _schedulers


def schedulers() -> Dict[str, Scheduler]:
    """
    Return all schedulers
    """
    return _schedulers


def shutdown_schedulers():
    """
    Terminate all registered schedulers and ask each one to cleanup their
    current state. This is synchronous, thus blocking the main process.
    """
    for name, scheduler in _schedulers.items():
        shutdown = getattr(scheduler, "shutdown", None)
        if shutdown:
            shutdown()


def is_scheduler_registered(name: str) -> bool:
    """
    Check if the given shceduler is registered
    """
    return name in _schedulers
