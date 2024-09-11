from datetime import timedelta

from pydantic import BaseModel


class JobSettings(BaseModel):
    is_enabled: bool
    debug: bool = False


class PeriodicJobSettings(JobSettings):
    check_interval: timedelta
