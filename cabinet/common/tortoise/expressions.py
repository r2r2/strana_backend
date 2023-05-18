from pypika import Case
from tortoise import Model
from pypika.functions import Sum
from tortoise.fields import Field
from tortoise.expressions import F
from tortoise.functions import Function
from pypika.queries import Selectable, Table
from pypika.terms import ArithmeticExpression
from typing import Optional, Any, Type, Union
from tortoise.query_utils import QueryModifier, Q


class OuterRef(F):
    """
    Outer related values
    """

    def __init__(self, name: str, alias: Optional[str] = None, table: Optional[str] = None) -> None:
        super().__init__(name=name, alias=alias)
        self.name: str = name
        self.table: Selectable = Selectable(table)

    def get_sql(self, **kwargs: Any) -> str:
        return super().get_sql(**kwargs)


class SumDefault(Function):
    """
    Sum with default case value
    """

    database_func: Sum = Sum
    populate_field_object: bool = True

    def __init__(
        self,
        field: Union[str, F, ArithmeticExpression],
        *default_values: Any,
        distinct: bool = False,
        _filter: Optional[Q] = None,
        case_default: Optional[Any] = None
    ) -> None:
        super().__init__(field, *default_values)
        self.distinct: bool = distinct
        self.filter: Union[Q, None] = _filter
        self.case_default: Any = case_default

    def _get_function_field(
        self, field: "Union[ArithmeticExpression, Field, str]", *default_values
    ) -> Function:
        if self.distinct:
            return self.database_func(field, *default_values).distinct()
        return self.database_func(field, *default_values)

    def _resolve_field_for_model(self, model: "Type[Model]", table: Table, field: str) -> dict:
        ret: dict = super()._resolve_field_for_model(model, table, field)
        if self.filter:
            modifier: QueryModifier = QueryModifier()
            modifier &= self.filter.resolve(model, {}, {}, model._meta.basetable)
            where_criterion, joins, having_criterion = modifier.get_query_modifiers()
            ret["field"]: Case = Case().when(where_criterion, ret["field"]).else_(self.case_default)
        return ret
