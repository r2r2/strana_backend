import base64
import functools
import hashlib
import math
import re

from django.utils.hashable import make_hashable
from graphql import GraphQLError

first_cap_re = re.compile("(.)([A-Z][a-z]+)")
all_cap_re = re.compile("([a-z0-9])([A-Z])")


def to_snake_case(name):
    s1 = first_cap_re.sub(r"\1_\2", name)
    return all_cap_re.sub(r"\1_\2", s1).lower()


def floor(number, digits=0):
    if number is None:
        return None
    n = 10 ** -digits
    return round(math.floor(number / n) * n, digits)


def ceil(number, digits=0):
    if number is None:
        return None
    n = 10 ** -digits
    return round(math.ceil(number / n) * n, digits)


def rgetattr(obj, attr, *args):
    # noinspection PyShadowingNames
    def _getattr(obj, attr):
        if obj:
            return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))


def make_hash_sha256(o):
    hasher = hashlib.sha256()
    hasher.update(repr(make_hashable(o)).encode())
    return base64.b64encode(hasher.digest()).decode()


def transliterate(text: str) -> str:
    symbols = (
        u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
        u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA",
    )
    tr = {ord(a): ord(b) for a, b in zip(*symbols)}
    return text.translate(tr)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_REAL_IP")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[-1].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_utm_data(data: dict) -> dict:
    utm_data = {}
    utm_names = ("utm_medium", "utm_source", "utm_campaign", "utm_content", "utm_term")
    if any(data.get(name) for name in utm_names):
        for utm_name in utm_names:
            utm_data[utm_name] = data.get(utm_name)

    return utm_data


def collect_form_errors(form) -> list:
    form_errors = []
    for field, errors in form.errors.items():
        errors_list = []
        for error in errors:
            errors_list.append(error)
        form_errors.append({"field": field, "messages": errors_list})
    return form_errors


def get_quarter_from_month(month: int) -> int:
    if month not in set(range(1, 13)):
        raise ValueError("Incorrect month value")
    return (month - 1) // 3 + 1

import logging

class GraphQLLogFilter(logging.Filter):
    def filter(self, record):
        if record.exc_info:
            etype, _, _ = record.exc_info
            if etype == GraphQLError:
                return True
        if record.stack_info and 'GraphQLError' in record.stack_info:
            return True
        if record.msg and 'GraphQLError' in record.msg:
            return None
        return True
