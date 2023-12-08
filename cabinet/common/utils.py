import base64
import phonenumbers
from urllib import parse
from typing import TypeVar, Iterable, Optional, Any
from math import ceil
from re import sub
from functools import reduce
from random import choices as C
from random import randint as R
from typing import Union
from base64 import b64decode, b64encode

import sentry_sdk

from common.schemas import UrlEncodeDTO
from config import site_config, application_config
from string import ascii_letters, digits, punctuation
from mimetypes import guess_type


T = TypeVar("T")


def generate_code() -> str:
    code = f"{R(0, 9)}{R(0, 9)}{R(0, 9)}{R(0, 9)}"
    return code


def generate_password() -> str:
    sequence = f"{ascii_letters}{digits}{punctuation}"
    password = f'{"".join(C(sequence, k=15))}{"".join(C(digits, k=5))}'
    return password


def generate_simple_password() -> str:
    sequence = f"{ascii_letters}{digits}"
    password = f'{"".join(C(sequence, k=8))}'
    return password


def to_camel_case(name: str) -> str:
    components = name.split("_")
    return components[0] + "".join(x.capitalize() if x else "_" for x in components[1:])


def to_snake_case(name: str) -> str:
    s1 = sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def from_global_id(global_id: str) -> list[str]:
    return b64decode(global_id.encode("utf-8")).decode("utf-8").split(":")


def to_global_id(type: str, id: Union[str, int]) -> str:
    return b64encode(f"{type}:{str(id)}".encode("utf-8")).decode("utf-8")


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        if obj:
            return getattr(obj, attr, *args)

    return reduce(_getattr, [obj] + attr.split("."))


def get_hyperlink(path: str) -> str:
    hyperlink: str = f"https://{site_config['site_host']}{application_config['root_path']}{path}"
    return hyperlink


def partition_list(l: list[T], max_chunk_size: int) -> Iterable[list[T]]:
    partitions_count = ceil(len(l) / max_chunk_size)
    return (l[max_chunk_size * i : max_chunk_size * (i + 1)] for i in range(partitions_count))


def get_mimetype(url: str) -> Optional[str]:
    mimetype, encoding = guess_type(url)
    return mimetype


def size_to_byte(*, mb: int = 0, kb: int = 0, b: int = 0) -> int:
    return b + (kb * 1024) + (mb * 1024 ** 2)


def encode_auth(auth: str) -> str:
    """
    Encode auth from a URL suitable for an HTTP header.
    >>> str(encode_auth('username%3Apassword'))
    'dXNlcm5hbWU6cGFzc3dvcmQ='

    Long auth strings should not cause a newline to be inserted.
    >>> long_auth = 'username:' + 'password'*10
    >>> chr(10) in str(encode_auth(long_auth))
    False
    """
    auth_s = parse.unquote(auth)
    # convert to bytes
    auth_bytes = auth_s.encode()
    encoded_bytes = base64.b64encode(auth_bytes)
    # convert back to a string
    encoded = encoded_bytes.decode()
    # strip the trailing carriage return
    return encoded.replace('\n', '')


def parse_phone(phone: str) -> Optional[str]:
    """
    Обработка телефонного номера, с учетом цифры 8 для РФ

    :returns: номер в формате E164 или None
    """

    # Если телефон начинается с 8 и скорее всего это телефон рф, введённый в национальном формате
    if phone.startswith("8"):
        phone: str = phone.replace("8", "+7", 1)
    elif phone.startswith("7"):
        phone: str = f"+{phone}"

    try:
        phone: phonenumbers.phonenumber.PhoneNumber = phonenumbers.parse(phone)
    except phonenumbers.NumberParseException:
        return None

    if not phonenumbers.is_valid_number(phone):
        return None

    return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)


def postfix_exclusions():
    return [
        "in",
        "gt",
        "lt",
        "lte",
        "gte",
        "not",
        "exact",
        "range",
        "iexact",
        "isnull",
        "not_in",
        "endswith",
        "contains",
        "icontains",
        "iendswith",
        "startswith",
        "not_isnull",
        "istartswith",
    ]


def convert_str_to_int(value: str | None) -> int | None:
    if value is None:
        return
    try:
        return int(value)
    except ValueError:
        try:
            return round(float(value))
        except ValueError as exception:
            sentry_sdk.capture_exception(exception)


def generate_notify_url(url_dto: UrlEncodeDTO) -> str:
    """
    Генерация url для уведомлений с учетом query параметров
    """
    query_separator_ascii: str = "%26"
    query_separator: str = "&"

    base_url: str = "https://{host}".format(host=url_dto.host)

    route_params: list[str] = url_dto.route_params
    if not route_params: # список пустой
        route_url: str = url_dto.route_template
    else: # список не пустой, надо изменить route по параметрам
        route_url: str = url_dto.route_template.format(*route_params) 

    query_params_dict: dict[str, Any] = url_dto.query_params or dict()
    query_params_list: list[str] = [f"{key}={value}" for key, value in query_params_dict.items()]
    if url_dto.use_ampersand_ascii:
        query_params: str = query_separator_ascii.join(query_params_list)
    else:
        query_params: str = query_separator.join(query_params_list)

    if len(query_params_dict) != 0:
        url: str = f"{base_url}{route_url}?{query_params}"
    else:
        url: str = f"{base_url}{route_url}"

    return url
