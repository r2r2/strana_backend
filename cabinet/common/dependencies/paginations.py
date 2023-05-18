from typing import Optional
from urllib.parse import urlparse, parse_qs, ParseResult

from fastapi import Query, Request

from common.paginations import PagePagination


class Pagination:
    """
    Пагинатор
    """

    def __init__(self, page_size: int = 12) -> None:
        self.page_size: int = page_size

    def __call__(
            self,
            request: Request,
            page: Optional[int] = Query(1, gt=0),
            page_size: Optional[int] = Query(None, gt=1, le=1000)
    ) -> PagePagination:
        path: str = request.scope["path"]
        parsed_url: ParseResult = urlparse(str(request.url))
        query: dict = parse_qs(parsed_url.query)
        page_size: int = page_size or self.page_size
        return PagePagination(path=path, query=query, page_number=page, page_size=page_size)
