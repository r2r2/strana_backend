from typing import Any

from pydantic.utils import GetterDict


class RecordGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        return self._obj[key] or default


class СhangeableGetterDict:
    """
    Hack to make object's smell just enough like dicts for root_validator.
    """

    __slots__ = ('_obj', '_overrides')

    def __init__(self, obj: Any):
        self._obj = obj
        self._overrides: dict | None = None

    def __setitem__(self, key, value):
        if self._overrides is None:
            self._overrides = {}
        self._overrides.__setitem__(key, value)

    def get(self, item: Any, default: Any = None) -> Any:
        if self._overrides is None:
            return getattr(self._obj, item, default)
        return self._overrides.get(item) or getattr(self._obj, item, default)
