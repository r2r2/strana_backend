from datetime import timedelta

from src.jobs.base_settings import PeriodicJobSettings


class AutoclosePrivateChatsSettings(PeriodicJobSettings):
    check_interval: timedelta
    close_after: timedelta
