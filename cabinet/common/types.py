from asyncio import Protocol
from typing import Union


class IAsyncFile(Protocol):
    async def write(self, data: Union[bytes, str]) -> None:
        ...

    async def read(self, size: int = -1) -> Union[bytes, str]:
        ...

    async def seek(self, offset: int) -> None:
        ...

    async def close(self) -> None:
        ...
