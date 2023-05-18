from tortoise import Model
from typing import Any, Type, Union, Optional
from ..utils import rgetattr


class ConverterBuilder(object):
    """
    Coverts mapped objects
    """

    def __init__(self, model: Type[Model]) -> None:
        self.model: Type[Model] = model

    def map(
        self, objects: Union[Type[Model], list[Type[Model]]], to: str, value: Any
    ) -> Union[Type[Model], list[Type[Model]]]:
        if isinstance(objects, list):
            for object in objects:
                setattr(object, to, value)
        else:
            setattr(objects, to, value)
        return objects

    def denormalize(
        self,
        bases: Union[Type[Model], list[Type[Model]]],
        objects: Union[Type[Model], list[Type[Model]]],
        to: Optional[str] = None,
        source: Optional[str] = None,
        update: Optional[bool] = False,
        pattern: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[dict[str, Any]]]:
        if update and objects is not None and pattern is None:
            if isinstance(bases, list):
                for base in bases:
                    self._update(base, to, objects)
            else:
                self._update(bases, to, objects)
        else:
            if isinstance(bases, list):
                for base in bases:
                    if not objects and source:
                        objects: Union[Type[Model], list[Type[Model]]] = getattr(base, source)
                    if not objects:
                        result = None
                    elif isinstance(objects, list):
                        result: dict[str, Any] = self._iterable_case(
                            pattern=pattern, target=objects
                        )
                    else:
                        result: dict[str, Any] = self._single_case(pattern=pattern, target=objects)
                    if update:
                        self._update(base, to, result)
            else:
                if not objects and source:
                    objects: Union[Type[Model], list[Type[Model]]] = getattr(bases, source)
                if not objects:
                    result = objects
                elif isinstance(objects, list):
                    result: dict[str, Any] = self._iterable_case(pattern=pattern, target=objects)
                else:
                    result: dict[str, Any] = self._single_case(pattern=pattern, target=objects)
                if update:
                    self._update(bases, to, result)
        return bases

    def _update(
        self, base: Union[Type[Model], list[Type[Model]]], to: str, result: dict[str, Any]
    ) -> None:
        setattr(base, to, result)

    def _iterable_case(
        self, pattern: dict[str, Any], target: list[Type[Model]]
    ) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = list()
        for objective in target:
            splat: dict[str, Any] = dict()
            for res_source, init_source in pattern.items():
                pointed: list[str] = ".".join(init_source.split("__")[1:])
                if pointed:
                    splat[res_source]: Any = rgetattr(objective, pointed)
                else:
                    splat[res_source]: Any = objective
            result.append(splat)
        return result

    def _single_case(self, pattern: dict[str, Any], target: Type[Model]) -> dict[str, Any]:
        result: dict[str, Any] = dict()
        for res_source, init_source in pattern.items():
            pointed: list[str] = ".".join(init_source.split("__")[1:])
            if pointed:
                result[res_source]: Any = rgetattr(target, pointed)
            else:
                result[res_source]: Any = target
        return result
