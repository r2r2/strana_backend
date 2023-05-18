from asyncio import Future, Task
from typing import Type, NamedTuple, Any, Union, Callable, Coroutine, Optional

from common.cor_handlers import AbstractCORHandler
from common.entities import BaseFilter


class SpecsGetAttributeHandler(AbstractCORHandler):

    def __init__(self, class_: Type[BaseFilter], state_class: Type[NamedTuple]):
        self.class_filter = class_
        self.repo = self.class_filter.Filter.repo()

        self.state_class = state_class

    async def handle(self) -> 'SpecsGetAttributeHandler.state':
        labels_mapping: dict[str, Any] = getattr(self.class_filter.Filter, "labels", dict())
        specs_overrides: dict[str, Any] = getattr(self.class_filter.Filter, "specs_overrides", dict())
        range_fields: Union[list[str], tuple[str, ...]] = getattr(self.class_filter.Filter, "ranges", list())
        choice_fields: Union[list[str], tuple[str, ...]] = getattr(
            self.class_filter.Filter, "choices", list()
        )
        exclude_fields: Union[list[str], tuple[str, ...]] = getattr(
            self.class_filter.Filter, "exclude", list()
        )
        ordering_fields: dict[str, Any] = getattr(
            getattr(self.class_filter, "Order", object()), "fields", dict()
        )

        choices_serializer: Optional[Callable[..., Coroutine]] = None

        if choice_fields:
            choices_serializer = self._get_choice_serializer()

        aliases: list[str] = list()
        choices: list[Union[Coroutine, Future, Task]] = list()
        ordering: list[dict[str, Any]] = list()
        return self.state_class(
            class_=self.class_filter,
            repo=self.repo,
            labels_mapping=labels_mapping,
            specs_overrides=specs_overrides,
            range_fields=range_fields,
            choice_fields=choice_fields,
            exclude_fields=exclude_fields,
            ordering_fields=ordering_fields,
            choices_serializer=choices_serializer,
            aliases=aliases,
            choices=choices,
            ordering=ordering,
        )

    def _get_choice_serializer(self) -> Callable[..., Coroutine]:
        choices_serializer: Callable[..., Coroutine] = getattr(
            self.class_filter.Filter, "choices_serializer", None
        )

        if not choices_serializer:
            async def choices_serializer(
                    field: str, queryset: Any, conditions: dict[str, Any]
            ) -> list[dict[str, Any]]:
                query_choices: list[Any] = await self.repo.specs(
                    field=field, choices=True, filters=conditions, queryset=queryset
                )
                serialized_choices: list[dict[str, Any]] = list(
                    choice.dict() for choice in query_choices
                )
                return serialized_choices
        return choices_serializer
