from typing import AsyncGenerator, Optional

from botocore.exceptions import DataNotFoundError

from .files import ProcessedFile, FileCategory, FileContainer

from ..boto import BotoStorage


class FileClient(object):
    """
    Клиент для стриминга файлов из контейнеров.
    """

    def __init__(self) -> None:
        self._boto: BotoStorage = BotoStorage()

    def __call__(
        self,
        container: FileContainer,
        category: str,
        index: int = -1,
        chunk_size: Optional[int] = 4096,
    ) -> AsyncGenerator[bytes, None]:
        try:
            category: FileCategory = next(
                filter(lambda _category: _category.slug == category, container)
            )
        except StopIteration:
            raise ValueError(f'Не найдена категория файлов "{category}"')

        file: ProcessedFile = category[index]
        try:
            return self._boto.stream_file(file.source, chunk_size=chunk_size)
        except DataNotFoundError:
            raise ValueError("Указанный файл не найден")
