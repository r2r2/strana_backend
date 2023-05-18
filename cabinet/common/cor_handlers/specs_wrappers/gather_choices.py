from asyncio import ensure_future
from typing import Any, Union, Callable, Coroutine, Tuple, Dict

from common.cor_handlers import AbstractCORHandler
from common.cor_states.wrappers import WrapperSpecsState
from common.utils import postfix_exclusions


class SpecsGatherChoicesHandler(AbstractCORHandler):
    def __init__(self, state: WrapperSpecsState):
        self.state: WrapperSpecsState = state

    def handle(
            self,
            additions,
            group,
            base_queryset,
    ) -> 'AbstractCORHandler.state':

        for name, info in self.state.class_.__fields__.items():

            if name not in self.state.exclude_fields:
                addition_filters: dict[str, Any] = additions.get(name, dict())
                name_components: list[str] = name.split("__")
                if name_components[-1] in postfix_exclusions():
                    name: str = "__".join(name_components[:-1])
                filters, label, alias = self._get_inner_attributes(addition_filters, name, info)
                overrided: Union[Callable[..., Coroutine], None] = self.state.specs_overrides.get(alias)

                if overrided and not isinstance(overrided, staticmethod):
                    self._override_case(
                        overrided=overrided,
                        group=group,
                        base_queryset=base_queryset,
                        addition_filters=addition_filters
                    )
                elif alias in self.state.choice_fields:
                    self._alias_in_choice_case(
                        name=name,
                        base_queryset=base_queryset,
                        filters=filters
                    )
                elif alias in self.state.range_fields:
                    if alias not in self.state.aliases:
                        self._alias_in_range_case(
                            name=name,
                            base_queryset=base_queryset,
                            filters=filters,
                            group=group
                        )
                else:
                    self._default_case(
                        name=name,
                        base_queryset=base_queryset,
                        filters=filters,
                        label=label,
                        group=group
                    )

                if alias not in self.state.aliases:
                    self.state.aliases.append(alias)
        return self.state

    def _get_inner_attributes(self, addition_filters, name, info) -> Tuple[Dict, str, str]:
        """ Возвращаем фильтры, заголовок, привязку"""
        alias: str = info.alias
        if "min" in alias or "max" in alias:
            alias: str = info.alias[:alias.find("_")]
        label: str = self.state.labels_mapping.get(alias)

        filters: dict[str, Any] = {f"{name}__isnull": False, **addition_filters}
        if label:
            filters[f"{label}__isnull"]: bool = False

        return filters, label, alias

    def _override_case(self, overrided, group, base_queryset, addition_filters) -> None:
        """Обработчик случая с переписанным параметром фетча"""
        self.state.choices.append(
            ensure_future(
                overrided(
                    repo=self.state.repo,
                    group=group,
                    queryset=base_queryset,
                    addition=addition_filters,
                )
            )
        )

    def _alias_in_choice_case(self, name, base_queryset, filters) -> None:
        """Обработчик случая с изменным сериалайзером"""
        self.state.choices.append(
            ensure_future(
                self.state.choices_serializer(
                    field=name, queryset=base_queryset, conditions=filters
                )
            )
        )

    def _alias_in_range_case(self, name, base_queryset, filters, group) -> None:
        """Обработчик случая с изменным диапазоном"""
        self.state.choices.append(
            ensure_future(
                self.state.repo.specs(
                    field=name,
                    queryset=base_queryset,
                    filters=filters,
                    ranges=True,
                    group=group,
                )
            )
        )

    def _default_case(self, name, base_queryset, filters, label, group) -> None:
        """Обработчик общего случая"""
        self.state.choices.append(
            ensure_future(
                self.state.repo.specs(
                    field=name,
                    queryset=base_queryset,
                    filters=filters,
                    label=label,
                    group=group,
                )
            )
        )
