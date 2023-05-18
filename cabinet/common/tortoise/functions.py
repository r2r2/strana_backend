from typing import Union, Any, Type

from pypika import functions, Table
from pypika.terms import ArithmeticExpression
from tortoise import Model
from tortoise.expressions import F
from tortoise.functions import Function


class Concat(Function):
    """
    Returns concatenated string

    :samp:`Concat("{FIELD_NAME}")`
    """

    database_func = functions.Concat
    populate_field_object = True

    def __init__(self, *fields: Union[str, F, ArithmeticExpression]) -> None:
        self.fields: list[Union[str, F, ArithmeticExpression]] = fields

    def resolve(self, model: Type[Model], table: Table) -> dict[str, Any]:
        fields: list[Union[str, F, ArithmeticExpression]] = list()
        for field in self.fields:
            fields.append(F.resolver_arithmetic_expression(model, field)[0])
        result: dict[str, Any] = dict(joins=list(), field=self.database_func(*fields))
        return result
