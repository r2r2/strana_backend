from datetime import date, datetime, timezone
from time import time


def timestamp_now() -> int:
    return int(time())


def datetime_now() -> datetime:
    return datetime.now(timezone.utc)


def start_of_day(date_: date) -> datetime:
    return datetime(year=date_.year, month=date_.month, day=date_.day, tzinfo=timezone.utc)


def end_of_day(date_: date) -> datetime:
    return datetime(
        year=date_.year,
        month=date_.month,
        day=date_.day,
        hour=23,
        minute=59,
        second=59,
        microsecond=999,
        tzinfo=timezone.utc,
    )
