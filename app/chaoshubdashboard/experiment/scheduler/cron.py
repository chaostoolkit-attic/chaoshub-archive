# -*- coding: utf-8 -*-
from tempfile import NamedTemporaryFile
import uuid

from crontab import CronTab

from ..types import ScheduleContext, ScheduleInfo

__all__ = ["CronScheduler"]


class CronScheduler:
    name = "cron"
    description = "Cron scheduler for local repeatable executions"
    version = "0.1.0"
    settings_key_prefix = "SCHED_CRON_"

    def __init__(self):
        self.cron = CronTab(user=True)
        self.jobs = {}

    def shutdown(self):
        for job in self.jobs.items():
            job.clear()
        self.cron.write()

    def cancel(self, job_id: str):
        job = self.jobs.pop(job_id, None)
        if job:
            job.clear()
            self.cron.write()

    def schedule(self, context: ScheduleContext) -> ScheduleInfo:
        org_name = context.get("org", {}).get("name")
        workspace_name = context.get("workspace", {}).get("name")
        experiment = context.get("experiment")

        with NamedTemporaryFile() as f:
            f.write(experiment)
            job = self.cron.new(
                command='chaos run --org "{}" --workspace "{}" {}'.format(
                    org_name, workspace_name, f.name
                )
            )
            job_id = str(uuid.uuid4)
            self.jobs[job_id] = job
            self.cron.write()

            return {
                "scheduler": CronScheduler.name,
                "job_id": job_id
            }
