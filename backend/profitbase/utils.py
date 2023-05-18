from datetime import datetime

import pytz
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from .constants import NEGATIVE_VALUES, POSITIVE_VALUES


def make_hashable(o):
    if isinstance(o, (tuple, list)):
        return tuple((make_hashable(e) for e in o))

    if isinstance(o, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in o.items()))

    if isinstance(o, (set, frozenset)):
        return tuple(sorted(make_hashable(e) for e in o))

    return o


def parse_bool(value):
    if type(value) == str:
        value = value.strip().lower()

    if value in NEGATIVE_VALUES:
        return False
    elif value in POSITIVE_VALUES:
        return True
    else:
        return bool(value)


def parse_int(value):
    if type(value) == str:
        value = value.strip()

    try:
        return int(value)
    except:
        if value in NEGATIVE_VALUES or not value:
            return 0
        else:
            return 1


def parse_datetime(dt, tz):
    if not dt:
        return

    return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=pytz.timezone(tz))


def get_image(url):
    if not url:
        return None

    img = NamedTemporaryFile(delete=True)
    res = requests.get(url)
    if res.ok:
        img.write(res.content)
        img.flush()
        return File(img)
    else:
        return None
