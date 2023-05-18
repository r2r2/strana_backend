from asyncio import Task, gather, create_task
from typing import Optional, Any, Type, Union, Coroutine, Generator

from ..mixins import Choices
from ..boto import BotoStorage
from .files import ProcessedFile, FileCategory, FileContainer


class FileProcessor:
    """
    Files processor
    """

    def __init__(
        self,
        path: str,
        files: dict[str, Any],
        choice_class: Type[Choices],
        container: Optional[FileContainer[FileCategory[ProcessedFile]]] = None,
        filter_by_hash: bool = True,
    ) -> None:
        self._path: str = path
        self._boto: BotoStorage = BotoStorage()
        self._choice_class: Type[Choices] = choice_class

        self._read_tasks: list[Task] = []

        self._files: dict[str, Any] = files
        self._filter_by_hash: bool = filter_by_hash

        if container is not None:
            self._container: FileContainer[FileCategory[ProcessedFile]] = container
        else:
            self._container: FileContainer[FileCategory[ProcessedFile]] = FileContainer()

    def __await__(self) -> Generator[Any, None, Any]:
        return self().__await__()

    async def __call__(self) -> FileContainer[FileCategory[ProcessedFile]]:
        gen_results: list[tuple[FileCategory[ProcessedFile], ProcessedFile, Coroutine]] = []
        for init_category in self._container:
            if category_files := self._files.pop(init_category.slug, []):
                category_gen: Generator = self._process_category(
                    init_category=init_category, category_files=category_files
                )
                for res in category_gen:
                    gen_results.append(res)
        for category, category_files in self._files.items():
            category_choice: Choices = self._choice_class(value=category)
            init_category: FileCategory[ProcessedFile] = FileCategory(
                count=0,
                name=category_choice.label,
                slug=category_choice.value,
            )
            category_gen: Generator = self._process_category(
                init_category=init_category, category_files=category_files
            )
            for res in category_gen:
                gen_results.append(res)
            self._container.append(init_category)

        await gather(*self._read_tasks)

        for category, file, boto_coro in gen_results:
            unique: bool = category.append(file, self._filter_by_hash)
            if unique:
                create_task(boto_coro)

        return self._container

    def _process_category(
        self, init_category: FileCategory[ProcessedFile], category_files: Union[list[Any], None]
    ) -> Generator:
        """Process category generator"""

        if category_files:
            for file in category_files:
                preprocessed_file: ProcessedFile = ProcessedFile.init_from_file(
                    file=file, path=self._path
                )
                processed_file, read_task, boto_coro = preprocessed_file.process(
                    file=file, boto=self._boto
                )
                self._read_tasks.append(read_task)
                yield init_category, processed_file, boto_coro


class FileDestroyer:
    """
    File destroyer
    """

    def __init__(
        self, files: dict[str, Any], container: FileContainer[FileCategory[ProcessedFile]]
    ) -> None:
        self._files: dict[str, Any] = files
        self._boto: BotoStorage = BotoStorage()
        self._container: FileContainer[FileCategory[ProcessedFile]] = container

    def __await__(self) -> Generator[Any, None, Any]:
        return self().__await__()

    async def __call__(self) -> FileContainer[FileCategory[ProcessedFile]]:
        for category in self._container:
            for _hash in self._files:
                if file := category.files_map.get(_hash):
                    category.pop(_hash)
                    create_task(file.delete(boto=self._boto))
        return self._container
