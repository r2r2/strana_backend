from typing import Any
from tortoise.expressions import Subquery
from pypika.queries import Selectable, QueryBuilder, Function


class FilteredSubquery(Subquery):
    """
    Filtered subquery
    """

    def __init__(self, *args, **kwargs) -> None:
        self.filters: dict[str, Any] = kwargs.pop("filters", dict())
        if self.filters is None:
            self.filters: dict[str, Any] = dict()
        super().__init__(*args, **kwargs)


class Exists(FilteredSubquery):
    """
    Exists subquery
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.field: Function = None

    def as_(self, alias: str) -> Selectable:
        query: QueryBuilder = self.query.as_query()
        self.field: Function = Function(alias)

        def _field_sql(*args: Any, **kwargs: Any) -> str:
            return f'"{alias}"'

        def _get_sql(*args: Any, **kwargs: Any):
            return f'EXISTS{self.get_sql(*args, **kwargs)} "{alias}"'

        setattr(query, "get_sql", _get_sql)
        setattr(self.field, "get_sql", _field_sql)
        return query.as_(alias)

    def get_sql(self, **kwargs: Any) -> str:
        return super().get_sql(**kwargs)

    def resolve(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return dict(field=self.field)


class SCount(FilteredSubquery):
    """
    Count subquery
    """

    def as_(self, alias: str) -> Selectable:
        query: QueryBuilder = self.query.as_query()

        def _get_sql(*args: Any, **kwargs: Any):
            sql: str = f'(SELECT COUNT(*) FROM {self.get_sql(*args, **kwargs)} "__{alias}") "{alias}"'
            if self.filters:
                wheres: str = str()
                for field, value in self.filters.items():
                    wheres += f'"__{alias}"."{field}"={value} AND'
                wheres: str = wheres[:-4]
                sql: str = f'(SELECT COUNT(*) FROM {self.get_sql(*args, **kwargs)} "__{alias}" WHERE {wheres}) "{alias}"'
            return sql

        setattr(query, "get_sql", _get_sql)
        return query.as_(alias)

    def get_sql(self, **kwargs: Any) -> str:
        return super().get_sql(**kwargs)
