# pylint: disable-all
from asyncio import Future, Task, ensure_future, gather
from copy import copy
from functools import wraps
from inspect import Parameter, Signature, iscoroutinefunction, signature
from typing import (Any, Awaitable, Callable, Coroutine, Optional, Type,
                    TypeVar, Union)

from fastapi import Depends, Form, Query
from pydantic import BaseModel
from pydantic.fields import ModelField
from tortoise import Model
from tortoise.exceptions import IntegrityError, TransactionManagementError

from .cor_handlers.specs_wrappers.gather_choices import \
    SpecsGatherChoicesHandler
from .cor_handlers.specs_wrappers.get_attributes import \
    SpecsGetAttributeHandler
from .cor_handlers.specs_wrappers.get_orders import SpecsOrdersHandler
from .cor_handlers.specs_wrappers.get_result import SpecsFormResultDictHandler
from .cor_states.wrappers import WrapperSpecsState
from .entities import BaseFilter
from .options import InitOption, RequestOption

T = TypeVar("T")


def mark_async(obj: T) -> T:
    """
    Uses __ainit__ instead of __init__ and allows class to be async
    """

    if obj.__new__ is object.__new__:
        cls_new: Union[Coroutine, Awaitable] = _new
    else:
        cls_new: Union[Coroutine, Awaitable] = _force_async(obj.__new__)

    @wraps(obj.__new__)
    async def new(cls, *args, **kwargs) -> object:
        self: object = await cls_new(cls, *args, **kwargs)

        if hasattr(self, "__ainit__"):
            cls_init: Union[Awaitable, Coroutine] = _force_async(self.__ainit__)
        else:
            cls_init: Union[Awaitable, Coroutine] = _force_async(self.__init__)
        await cls_init(*args, **kwargs)

        return self

    obj.__new__ = new

    return obj


def as_form(cls: Type[BaseModel]) -> Type[BaseModel]:
    """
    Allows to use pydantic model as form object
    """
    new_parameters: list[Parameter] = list()

    for field_name, model_field in cls.__fields__.items():
        model_field: ModelField
        if not model_field.required:
            new_parameters.append(
                Parameter(
                    model_field.alias,
                    Parameter.POSITIONAL_ONLY,
                    default=Form(model_field.default),
                    annotation=model_field.outer_type_,
                )
            )
        else:
            new_parameters.append(
                Parameter(
                    model_field.alias,
                    Parameter.POSITIONAL_ONLY,
                    default=Form(...),
                    annotation=model_field.outer_type_,
                )
            )

    async def as_form_coro(**data: dict[str, Any]) -> BaseModel:
        return cls(**data)

    sig: Signature = signature(as_form_coro)
    sig: Signature = sig.replace(parameters=new_parameters)
    as_form_coro.__signature__ = sig
    setattr(cls, "as_form", as_form_coro)
    return cls


def filterize(cls: Type[BaseFilter]) -> Type[BaseFilter]:
    """
    Allows to user pydantic model as query object
    """
    assert hasattr(cls, "Filter")
    assert hasattr(cls.Filter, "repo")

    credentials: Union[Any, None] = getattr(cls, "Credentials", None)

    postfix_exclusions: list[str] = [  # chechk facets. redo it for cor and delete this property
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
    repo: Any = cls.Filter.repo()
    new_parameters: list[Parameter] = list()

    for field_name, model_field in cls.__fields__.items():
        model_field: ModelField
        default = ...
        if not model_field.required:
            default = model_field.default
        new_parameters.append(
            Parameter(
                model_field.alias,
                Parameter.POSITIONAL_ONLY,
                default=Query(default, description=model_field.field_info.description),
                annotation=model_field.outer_type_,
            )
        )

    if credentials:
        credentials_options: dict[str, Any] = getattr(credentials, "options", None)
        if credentials_options:
            for field_name, field_info in credentials_options.items():
                new_parameters.append(
                    Parameter(
                        field_name,
                        Parameter.POSITIONAL_ONLY,
                        default=Depends(field_info["callable"]),
                    )
                )

    async def filterize_coro(**data: dict[str, Any]) -> dict[str, Any]:
        initialized: BaseFilter = cls(**data)
        filters: dict[str, Any] = dict()
        additions: dict[str, list[Union[InitOption, RequestOption]]] = getattr(
            initialized.Filter, "additions", dict()
        )
        for field, value in initialized.dict(exclude_none=True, exclude_unset=True).items():
            if value is not None:
                filters[field]: Any = value
                addition: dict[str, Any] = additions.get(field, list())
                additional_filters: dict[str, Any] = dict()
                for f in addition:
                    if isinstance(f, InitOption):
                        additional_filters.update(f.as_filter())
                    elif isinstance(f, RequestOption):
                        option: Any = data.get(str(f))
                        if option is None:
                            for or_option in f.choices:
                                option: Any = data.get(str(or_option))
                                if option:
                                    additional_filters.update(or_option.as_filter(option))
                                    break
                        else:
                            additional_filters.update(f.as_filter(option))
                filters.update(additional_filters)
        return filters

    async def additions_coro(**data: dict[str, Any]) -> dict[str, Any]:
        filters: dict[str, Any] = dict()
        additions: dict[str, list[Union[InitOption, RequestOption]]] = getattr(
            cls.Filter, "additions", dict()
        )
        for field, addition in additions.items():
            filters[field]: dict[str, Any] = dict()
            for f in addition:
                if isinstance(f, InitOption):
                    filters[field].update(f.as_filter())
                elif isinstance(f, RequestOption):
                    option: Any = data.get(str(f))
                    if option is None:
                        for or_option in f.choices:
                            option: Any = data.get(str(or_option))
                            if option:
                                filters[field].update(or_option.as_filter(option))
                                break
                    else:
                        filters[field].update(f.as_filter(option))
        return filters

    sig: Signature = signature(filterize_coro)
    sig: Signature = sig.replace(parameters=new_parameters)
    filterize_coro.__signature__ = sig
    setattr(cls, "filterize", filterize_coro)

    sig: Signature = signature(additions_coro)
    sig: Signature = sig.replace(parameters=new_parameters)
    additions_coro.__signature__ = sig
    setattr(cls, "additions", additions_coro)

    async def specs_coro(
        additions: dict[str, Any] = Depends(cls.additions)
    ) -> Callable[..., Coroutine]:

        async def specs(
            group: str,
            detail: bool = False,
            q_filters: Optional[list[Any]] = None,
            filters: Optional[dict[str, Any]] = None,
        ) -> Callable[..., Coroutine]:
            if filters is None:
                filters: dict[str, Any] = dict()

            base_queryset: Any = repo.list(filters=filters, q_filters=q_filters)
            if detail:
                base_queryset: Any = repo.retrieve(filters=filters, q_filters=q_filters)

            state: WrapperSpecsState = await SpecsGetAttributeHandler(cls, WrapperSpecsState).handle()
            state = SpecsGatherChoicesHandler(state).handle(
                additions=additions,
                group=group,
                base_queryset=base_queryset
            )
            state = SpecsOrdersHandler(state).handle()
            return await SpecsFormResultDictHandler(state).handle()

        return specs

    async def facets_coro(
        additions: dict[str, Any] = Depends(cls.additions)
    ) -> Callable[..., Coroutine]:
        async def facets(
            group: str,
            detail: bool = False,
            q_filters: Optional[list[Any]] = None,
            filters: Optional[dict[str, Any]] = None,
        ):
            if filters is None:
                filters: dict[str, Any] = dict()

            filters.pop("ordering", None)

            future_count: Future = ensure_future(repo.scount(filters=filters, q_filters=q_filters))

            facets_overrides: dict[str, Any] = getattr(cls.Filter, "facets_overrides", dict())
            range_fields: Union[list[str], tuple[str, ...]] = getattr(cls.Filter, "ranges", list())
            choice_fields: Union[list[str], tuple[str, ...]] = getattr(
                cls.Filter, "choices", list()
            )
            exclude_fields: Union[list[str], tuple[str, ...]] = getattr(
                cls.Filter, "exclude", list()
            )

            if choice_fields:

                choices_serializer: Callable[..., Coroutine] = getattr(
                    cls.Filter, "choices_serializer", None
                )

                if not choices_serializer:

                    async def choices_serializer(
                        field: str, queryset: Any, conditions: dict[str, Any]
                    ) -> list[dict[str, Any]]:
                        query_choices: list[Any] = await repo.facets(
                            field=field, filters=conditions, queryset=queryset
                        )
                        serialized_choices: list[dict[str, Any]] = list(
                            choice.value for choice in query_choices
                        )
                        return serialized_choices

            aliases: list[str] = list()
            choices: list[Union[Coroutine, Future, Task]] = list()

            for name, info in cls.__fields__.items():

                if name not in exclude_fields:

                    qs_filters: dict[str, Any] = copy(filters)
                    qs_filters.pop(name, None)

                    base_queryset: Any = repo.list(filters=qs_filters, q_filters=q_filters)
                    if detail:
                        base_queryset: Any = repo.retrieve(filters=qs_filters, q_filters=q_filters)

                    alias: str = info.alias
                    if "min" in alias or "max" in alias:
                        alias: str = info.alias[: alias.find("_")]
                    name_components: list[str] = name.split("__")
                    if name_components[-1] in postfix_exclusions:
                        name: str = "__".join(name_components[:-1])

                    addition_filters: dict[str, Any] = additions.get(name, dict())

                    qs_filters: dict[str, Any] = {f"{name}__isnull": False, **addition_filters}
                    overrided: Union[Callable[..., Coroutine], None] = facets_overrides.get(alias)

                    if overrided and not isinstance(overrided, staticmethod):
                        choices.append(
                            ensure_future(
                                overrided(
                                    repo=repo,
                                    group=group,
                                    queryset=base_queryset,
                                    addition=addition_filters,
                                )
                            )
                        )

                    elif alias in choice_fields:
                        choices.append(
                            ensure_future(
                                choices_serializer(
                                    field=name, queryset=base_queryset, conditions=qs_filters
                                )
                            )
                        )
                    elif alias in range_fields:
                        if alias not in aliases:
                            choices.append(
                                ensure_future(
                                    repo.facets(
                                        field=name,
                                        queryset=base_queryset,
                                        filters=qs_filters,
                                        ranges=True,
                                        group=group,
                                    )
                                )
                            )
                    else:
                        choices.append(
                            ensure_future(
                                repo.facets(
                                    field=name,
                                    queryset=base_queryset,
                                    filters=qs_filters,
                                    group=group,
                                )
                            )
                        )
                    if alias not in aliases:
                        aliases.append(alias)

            counted: Union[list[tuple[Union[int, str]]], int] = await future_count
            if isinstance(counted, tuple) or isinstance(counted, list):
                count: int = len(counted)
                if count and count == 1:
                    count: int = counted[0][0]
            else:
                count: int = counted

            values: dict[str, Any] = dict(zip(aliases, await gather(*choices)))

            result: dict[str, Any] = dict(count=count, facets=values)
            return result

        return facets

    setattr(cls, "specs", specs_coro)
    setattr(cls, "facets", facets_coro)

    return cls


def transaction_handler(repo: type) -> type:
    """
    Fixes update or create is case of transaction abort
    """

    method: Callable[..., Awaitable] = getattr(repo, "update_or_create", None)
    if not method:
        raise AttributeError(f"{repo.__name__} does not implement update_or_create method.")

    method_annotations: dict[str, Any] = getattr(method, "__annotations__", None)
    if not method_annotations:
        raise AttributeError(f"Method {method.__name__} of {repo.__name__} is not type annotated.")

    returnable: Union[Type[Model], None] = method_annotations.get("return")
    if not returnable:
        raise AttributeError(
            f"Method {method.__name__} of {repo.__name__} is not type annotated with return."
        )

    async def handled_update_or_create(*args: Any, **kwargs: Any) -> Type[Model]:
        data: dict[str, Any] = kwargs.get("data")
        filters: dict[str, Any] = kwargs.get("filters")
        try:
            result: Type[Model] = await method(*args, **kwargs)
        except TransactionManagementError:
            try:
                result: Model = await returnable.create(**dict(**filters, **data))
            except IntegrityError:
                result: Model = await returnable.get(**filters)
                result: Model = result.update_from_dict(data=data)
                await result.save()
        return result

    setattr(repo, "update_or_create", handled_update_or_create)

    return repo


class classproperty:
    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self


def _force_async(method: Union[Coroutine, Callable[..., Coroutine]]) -> Callable[..., Coroutine]:
    """
    Forces method to be an awaitable object
    """
    if iscoroutinefunction(method):
        return method

    async def wrapped(*args, **kwargs):
        return method(*args, **kwargs)

    return wrapped


async def _new(cls, *args, **kwargs) -> object:
    """
    Async class creation implementation
    """
    return object.__new__(cls)
