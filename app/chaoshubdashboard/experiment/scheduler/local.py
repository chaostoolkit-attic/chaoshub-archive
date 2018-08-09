# -*- coding: utf-8 -*-
import json
import os
import subprocess
from tempfile import TemporaryDirectory
import threading
from typing import Dict
import uuid

from chaoshub.settings import set_chaos_hub_settings
from chaoslib.settings import load_settings, save_settings

from ..types import ScheduleContext, ScheduleInfo

__all__ = ["LocalScheduler"]

Tasks = Dict[str, 'LocalExecution']


class LocalScheduler:
    name = "local"
    description = "Local scheduler for one-shot executions"
    version = "0.1.0"
    settings_key_prefix = "SCHED_LOCAL_"

    def __init__(self, chaostoolkit_cli_path: str = "chaos") -> None:
        self.chaostoolkit_cli_path = os.path.expanduser(
            chaostoolkit_cli_path)
        self.tasks: Tasks = {}

    def shutdown(self):
        for pid, task in self.tasks.items():
            task.terminate()
        self.tasks.clear()

    def cancel(self, id: str):
        task = self.tasks.pop(id, None)
        if task:
            task.terminate()

    def schedule(self, context: ScheduleContext) -> ScheduleInfo:
        execution = LocalExecution(self.chaostoolkit_cli_path, context)
        self.tasks[execution.id] = execution
        execution.start()

        return {
            "scheduler": LocalScheduler.name,
            "id": execution.id
        }


class LocalExecution(threading.Thread):
    def __init__(self, chaostoolkit_cli_path: str,
                 context: ScheduleContext) -> None:
        threading.Thread.__init__(self)
        self.chaostoolkit_cli_path = chaostoolkit_cli_path
        self.id = str(uuid.uuid4())
        self.context = context
        self.proc = None

    def terminate(self):
        if self.proc and self.proc.poll() is not None:
            self.proc.terminate()

    def run(self):
        hub_url = self.context.get("hub_url")
        token = self.context.get("token")
        org_name = self.context.get("org", {}).get("name")
        workspace_name = self.context.get("workspace", {}).get("name")
        experiment = self.context.get("experiment")

        with TemporaryDirectory() as dname:
            settings_path = os.path.join(dname, "settings.yaml")
            settings = {}
            set_chaos_hub_settings(hub_url, token, settings)
            save_settings(settings, settings_path)

            experiment_path = os.path.join(dname, "experiment.json")
            with open(experiment_path, "w") as f:
                f.write(json.dumps(experiment["payload"]))

            cmd = [
                self.chaostoolkit_cli_path,
                '--settings',
                settings_path,
                'run',
                '--org', org_name,
                '--workspace', workspace_name,
                experiment_path
            ]

            self.proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=os.environ, cwd=dname)
            self.proc.wait()
