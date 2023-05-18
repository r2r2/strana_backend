from time import time
from hashlib import sha256
from config import aws_config
from asyncio import create_task, Future, Task
from typing import Union, Any, Optional, Generic, TypeVar, Generator, Coroutine

from ..boto import BotoStorage


FILE_CATEGORY = TypeVar("FILE_CATEGORY", bound="FileCategory")
PROCESSED_FILE = TypeVar("PROCESSED_FILE", bound="ProcessedFile")


class ProcessedFile(object):
    """
    Processed file
    """

    def __init__(
        self,
        aws: Optional[str] = None,
        name: Optional[str] = None,
        hash: Optional[str] = None,
        source: Optional[str] = None,
        bytes_size: Optional[int] = None,
        mb_size: Optional[int] = None,
        kb_size: Optional[int] = None,
        extension: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> None:
        self.aws: Optional[str] = aws
        self.name: Optional[str] = name
        self.hash: Optional[str] = hash
        self.source: Optional[str] = source
        self.bytes_size: Optional[int] = bytes_size
        self.mb_size: Optional[int] = mb_size
        self.kb_size: Optional[int] = kb_size
        self.extension: Optional[str] = extension
        self.content_type: Optional[str] = content_type

    def __str__(self) -> str:
        return self.name if self.name else super().__str__()

    @classmethod
    def init_from_file(cls, file: Any, path: str) -> "ProcessedFile":
        split_name = file.filename.split(".")
        hash: Optional[str] = None
        bytes_size: int = 0
        mb_size: int = 0
        kb_size: int = 0
        name: str = ".".join(split_name[:-1])
        content_type: str = file.content_type
        extension: str = split_name[-1]
        hashed_name: str = sha256(
            (".".join(file.filename.split(".")[:-1]) + str(int(time()))).encode("utf-8")
        ).hexdigest()
        source: str = f"{path}/{hashed_name}.{extension}"
        aws: str = f'{aws_config["endpoint_url"]}{aws_config["storage_bucket_name"]}/{source}'
        init_kwargs: dict[str, Any] = dict(
            aws=aws,
            name=name,
            hash=hash,
            source=source,
            bytes_size=bytes_size,
            mb_size=mb_size,
            kb_size=kb_size,
            extension=extension,
            content_type=content_type,
        )
        return cls(**init_kwargs)

    def process(self, file: Any, boto: BotoStorage) -> tuple["ProcessedFile", Task, Coroutine]:
        def read_callback(task_or_future: Union[Task, Future]) -> None:
            setattr(self, "hash", sha256(task_or_future.result()).hexdigest())
            setattr(self, "bytes_size", len(task_or_future.result()))
            setattr(self, "kb_size", round(len(task_or_future.result()) / 1024, 1))
            setattr(self, "mb_size", round(len(task_or_future.result()) / 1024**2, 1))

        read_task: Task = create_task(file.read())
        read_task.add_done_callback(read_callback)
        boto_coro: Coroutine = boto.upload_file(file, self.source)
        return self, read_task, boto_coro

    def delete(self, boto: BotoStorage) -> Coroutine:
        return boto.delete_file(source=self.source)

    def serializable(self) -> dict[str, Any]:
        result: dict[str, Any] = dict(
            aws=self.aws,
            name=self.name,
            hash=self.hash,
            source=self.source,
            bytes_size=self.bytes_size,
            mb_size=self.mb_size,
            kb_size=self.kb_size,
            extension=self.extension,
            content_type=self.content_type,
        )
        return result


class FileCategory(Generic[PROCESSED_FILE], list):
    """
    Container for processed files
    """

    def __init__(
        self, name: str, slug: str, count: int, files: Optional[Union[list[PROCESSED_FILE]]] = None
    ) -> None:
        self.name: str = name
        self.slug: str = slug
        self.count: int = count
        self.files_map: dict[str, PROCESSED_FILE] = dict()

        if files is not None:
            self.files: list[PROCESSED_FILE] = files
            for file in files:
                self.files_map[file.hash]: PROCESSED_FILE = file
        else:
            self.files: list[PROCESSED_FILE] = list()

    def __iter__(self) -> Generator[PROCESSED_FILE, None, None]:
        for file in self.files:
            yield file

    def __str__(self) -> str:
        files: str = str()
        breaker: str = "\n"
        double_tabular: str = "\t\t"
        triple_tabular: str = "\t\t\t"
        for file in self.files:
            files += f"{breaker}{triple_tabular}{str(file)}"
        representation: str = (
            f"{self.__class__.__name__}("
            f"{breaker}{triple_tabular}name={self.name},"
            f"{breaker}{triple_tabular}slug={self.slug},"
            f"{breaker}{triple_tabular}count={self.count},"
            f"{breaker}{triple_tabular}files=["
            f"{files}{breaker}{triple_tabular}]"
            f"{breaker}{double_tabular}"
            f")"
        )
        return representation

    def __bool__(self) -> bool:
        return bool(self.files)

    def __getitem__(self, index: int) -> PROCESSED_FILE:
        return self.files[index]

    def append(self, file: PROCESSED_FILE, filter_by_hash: bool = True) -> bool:
        """Добавление файла в категорию.

        Args:
            file: Файл.
            filter_by_hash: Добавлять ли одинаковые (по хешу) файлы в категорию или нет.
                True - они не будут добавлены. False - пофиг, фигачим все подряд.

        Returns:
            Был ли добавлен файл или нет.
        """
        result: bool = False
        if (filter_by_hash is True and file.hash not in self.files_map) or filter_by_hash is False:
            self.count += 1
            result: bool = True
            self.files.append(file)
            self.files_map[file.hash]: PROCESSED_FILE = file
        return result

    def pop(self, hash: str) -> bool:
        result: bool = False
        if file := self.files_map.pop(hash, None):
            self.count -= 1
            result: bool = True
            self.files.pop(self.files.index(file))
        return result

    def serializable(self) -> dict[str, Any]:
        result: dict[str, Any] = dict(
            name=self.name,
            slug=self.slug,
            count=self.count,
            files=list(file.serializable() for file in self.files),
        )
        return result


class FileContainer(Generic[FILE_CATEGORY], list):
    """
    Container for MutableDocumentContainerField
    """

    def __init__(self, categories: Optional[list[FILE_CATEGORY]] = None) -> None:
        if categories is not None:
            self.categories: list[FILE_CATEGORY] = categories
        else:
            self.categories: list[FILE_CATEGORY] = list()

    def __iter__(self) -> Generator[FILE_CATEGORY, None, None]:
        for category in self.categories:
            yield category

    def __bool__(self) -> bool:
        return bool(self.categories)

    def __getitem__(self, index: int) -> FILE_CATEGORY:
        return self.categories[index]

    def __str__(self) -> str:
        breaker: str = "\n"
        tabular: str = "\t"
        representation: str = str()
        for category in self:
            representation += f"{tabular}{str(category)},{breaker}"
        representation: str = f"[{breaker}{representation}{breaker}]"
        return representation

    def append(self, category: FILE_CATEGORY) -> None:
        self.categories.append(category)

    def serializable(self) -> list[dict[str, Any]]:
        return list(category.serializable() for category in self.categories)
