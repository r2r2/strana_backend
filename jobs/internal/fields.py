from collections.abc import Callable, Generator

from celery.schedules import crontab


class CronTab(str, crontab):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[str], crontab], None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> crontab:
        try:
            minute, hour, day_of_month, month_of_year, day_of_week = value.split()
            return crontab(
                minute=minute,
                hour=hour,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
                day_of_week=day_of_week,
            )
        except ValueError:
            raise ValueError(f"{value} is not valid crontab settings")
