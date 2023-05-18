from typing import Any

from pydantic.utils import GetterDict


class RecordGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        return self._obj[key] or default
