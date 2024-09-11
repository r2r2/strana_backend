from functools import partial
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema
from typing_extensions import get_args

from src.entities.users import Language

ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


class PaginatedResponse(BaseModel, Generic[ResponseModel]):
    count: int
    data: list[ResponseModel]


class CommaSeparatedNumbers[T](list[T]):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        def _parse_from_str(val_type: Any, value: str) -> list[int]:
            return [val_type(v) for v in value.split(",")]

        args = get_args(source_type)
        if not args:
            raise ValueError("CommaSeparatedNumbers must have a type argument")

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(partial(_parse_from_str, args[0])),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=from_str_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: ",".join([str(v) for v in instance])
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


class SportResponse(BaseModel):
    id: int
    name: str


class ChangeLanguageRequest(BaseModel):
    lang: Language
