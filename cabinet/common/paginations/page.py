from copy import copy
from enum import StrEnum
from typing import Any, Optional
from collections import OrderedDict

from config import site_config


class AllowedPageParams(StrEnum):
    ALL = 'all'


class PagePagination(object):
    """
    Page pagination
    """

    count_key: str = "count"
    url_template: str = "https://{}/api{}?page={}"
    dict_fields: tuple[str, str, str] = ("count", "next_page", "previous_page")

    def __init__(self, path: str, page_size: int, page_number: int, query: dict):
        self.path: str = path
        self.page_size: int = page_size
        self.page_number: int = page_number
        self.query: dict = copy(query)
        self.start: int = (page_number - 1) * page_size
        self.end: int = (page_number - 1) * page_size + page_size
        self.page_params: Optional[str] = self.query.get('page_params')

        self._init_page_params()
        self.query.pop("page", None)

    def __call__(self, count: int) -> OrderedDict[str, Any]:
        filters: str = str()
        next_page: Optional[str] = None
        previous_page: Optional[str] = None

        for key, values in self.query.items():
            for query in values:
                filters += f"&{key}={query}"
        if self.start:
            previous_page: str = (
                self.build_url(self.page_number - 1, extra=filters)
            )
        if count > self.end:
            next_page: str = (
                self.build_url(self.page_number + 1, extra=filters)
            )
        current_page: str = (
            self.build_url(self.page_number, extra=filters)
        )
        page_info: OrderedDict[str, Any] = OrderedDict(
            [
                ("total", int(count / self.page_size) + 1),
                ("query", filters[1:] if filters else None),
                ("next_page", next_page),
                ("current_page", current_page),
                ("previous_page", previous_page),
            ]
        )
        return page_info

    def _init_page_params(self):
        """
        Init custom page parameters
        params must be separated by comma.
        @return: None
        """
        if not isinstance(self.page_params, str):
            return
        page_params: list[str] = self.page_params.split(',')
        for param in page_params:
            if param.strip() == AllowedPageParams.ALL:
                self.start: int = 0
                self.page_number: int =  1
                self.page_size: int = 1000
                self.end: int = 1000

    def build_url(self, page_number: int, *, extra: str) -> str:
        """
        Build url for paginator
        @param page_number: int
        @param extra: str. Extra string for url
        @return: str
        """
        return self.url_template.format(site_config["site_host"], self.path, page_number) + extra

