from config import aws_config
from collections import OrderedDict
from typing import Any, Type, Union, Optional

from tortoise import Model, ConfigurationError
from tortoise.validators import MaxLengthValidator
from tortoise.fields import Field, CharField, JSONField

from .mixins import Choices
from .imgproxy import ImageProxy
from .files import ProcessedFile, FileCategory, FileContainer


class CharChoiceField(Field, str):
    """
    Char field with choices
    """

    def __init__(self, max_length: int, choice_class: Type[Choices], **kwargs):
        if int(max_length) < 1:
            raise ConfigurationError("'max_length' must be >= 1")
        self.max_length = int(max_length)
        self.choice_class: Type[Choices] = choice_class
        super().__init__(**kwargs)
        self.validators.append(MaxLengthValidator(self.max_length))

    def to_python_value(self, value: Any) -> Optional[Choices]:
        if value is not None and not isinstance(value, self.field_type):
            value: str = self.field_type(value)
        self.validate(value)
        choice: Optional[Choices] = None
        if value is not None:
            choice: Choices = self.choice_class(value=value)
        return choice

    def to_db_value(self, value: Any, instance: Union[Type[Model], Model]) -> Any:
        if isinstance(value, self.choice_class):
            value: Union[str, None] = value.value
        if value is not None and not isinstance(value, self.field_type):
            value = self.field_type(value)
        self.validate(value)
        return value

    @property
    def constraints(self) -> dict:
        return {"max_length": self.max_length}

    @property
    def SQL_TYPE(self) -> str:
        return f"VARCHAR({self.max_length})"


class SmallIntChoiceField(Field, int):
    """
    Small integer field with choices
    """

    SQL_TYPE = "SMALLINT"
    allows_generated = True

    def __init__(self, choice_class: Type[Choices], pk: bool = False, **kwargs) -> None:
        if pk:
            kwargs["generated"] = bool(kwargs.get("generated", True))
        self.choice_class: Type[Choices] = choice_class
        super().__init__(**kwargs)

    def to_python_value(self, value: Any) -> Choices:
        if value is not None and not isinstance(value, self.field_type):
            value: int = self.field_type(value)
        self.validate(value)
        choice: Choices = self.choice_class(value=value)
        return choice

    def to_db_value(self, value: Any, instance: Union[Type[Model], Model]) -> Any:
        if isinstance(value, self.choice_class):
            value: Union[int, str, None] = value.value
        if value is not None and not isinstance(value, self.field_type):
            value = self.field_type(value)
        self.validate(value)
        return value

    @property
    def constraints(self) -> dict:
        return {"ge": 1 if self.generated or self.reference else -32768, "le": 32767}

    class _db_postgres:
        GENERATED_SQL = "SMALLSERIAL NOT NULL PRIMARY KEY"

    class _db_sqlite:
        GENERATED_SQL = "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL"

    class _db_mysql:
        GENERATED_SQL = "SMALLINT NOT NULL PRIMARY KEY AUTO_INCREMENT"


class IntChoiceField(Field, int):
    """
    Integer field with choices
    """

    SQL_TYPE = "INT"
    allows_generated = True

    def __init__(
        self, choice_class: Type[Choices], pk: bool = False, **kwargs
    ) -> None:
        if pk:
            kwargs["generated"] = bool(kwargs.get("generated", True))
        self.choice_class: Type[Choices] = choice_class
        super().__init__(**kwargs)

    def to_python_value(self, value: Any) -> Choices:
        if value is not None and not isinstance(value, self.field_type):
            value: int = self.field_type(value)
        self.validate(value)
        choice: Choices = self.choice_class(value=value)
        return choice

    def to_db_value(self, value: Any, instance: Union[Type[Model], Model]) -> Any:
        if isinstance(value, self.choice_class):
            value: Union[int, str, None] = value.value
        if value is not None and not isinstance(value, self.field_type):
            value = self.field_type(value)
        self.validate(value)
        return value

    @property
    def constraints(self) -> dict:
        return {"ge": 1 if self.generated or self.reference else -2147483648, "le": 2147483647}

    class _db_postgres:
        GENERATED_SQL = "SERIAL NOT NULL PRIMARY KEY"

    class _db_sqlite:
        GENERATED_SQL = "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL"

    class _db_mysql:
        GENERATED_SQL = "INT NOT NULL PRIMARY KEY AUTO_INCREMENT"


class MediaField(CharField):
    """
    Media field
    """

    def to_python_value(self, value: str) -> Union[OrderedDict[str, Any], None]:
        value: Union[str, None] = super().to_python_value(value)
        if value:
            value: OrderedDict[str, Any] = OrderedDict(
                dict(
                    src=value,
                    s3=f's3://{aws_config["storage_bucket_name"]}/{value}',
                    aws=f'{aws_config["custom_domain"]}/{aws_config["storage_bucket_name"]}/{value}',
                    # proxy=ImageProxy(
                    #     s3_source=f's3://{aws_config["storage_bucket_name"]}/{value}'
                    # ).svg_to_png(),
                )
            )
        return value

    def to_db_value(self, value: Any, instance: Union[Type[Model], Model]) -> str:
        if value is not None and not isinstance(value, self.field_type):
            value: str = self.field_type(value["src"])
        self.validate(value)
        return value


class MutableDocumentContainerField(JSONField):
    """
    Mutable document container field
    """

    def to_python_value(
        self, value: Optional[Union[dict, list, str]]
    ) -> Optional[Union[dict, list]]:
        if isinstance(value, str):
            value: list[dict[str, Any]] = self.decoder(value)
            value: FileContainer[FileCategory[ProcessedFile]] = self._process_from_db_to_python(
                value=value
            )
        elif isinstance(value, FileContainer):
            value: FileContainer[FileCategory[ProcessedFile]] = value
        elif isinstance(value, list):
            value: FileContainer[FileCategory[ProcessedFile]] = self._process_from_db_to_python(
                value=value
            )
        else:
            value: FileContainer[FileCategory[ProcessedFile]] = FileContainer()
        return super().to_python_value(value=value)

    def to_db_value(
        self,
        value: Union[str, FileContainer[FileCategory[ProcessedFile]]],
        instance: Union[Type[Model], Model],
    ) -> Optional[str]:
        if isinstance(value, str):
            try:
                self.encoder(value)
            except Exception:
                value: list[dict[str, Any]] = list()
        elif isinstance(value, FileContainer):
            value: list[dict[str, Any]] = self._process_from_python_to_db(value=value)
        elif isinstance(value, list):
            value: list[dict[str, Any]] = value
        else:
            value: list[dict[str, Any]] = list()
        return super().to_db_value(value=value, instance=instance)

    @staticmethod
    def _process_from_db_to_python(value: list[dict[str, Any]]) -> FileContainer[FileCategory[ProcessedFile]]:
        container: FileContainer[FileCategory[ProcessedFile]] = FileContainer()
        for category in value:
            category_files = category.pop("files")
            transformed_files: list[ProcessedFile] = list()
            for file in category_files:
                if isinstance(file, ProcessedFile):
                    transformed_files.append(file)
                else:
                    transformed_files.append(ProcessedFile(**file))
            container.append(FileCategory(**category, files=transformed_files))
        value: FileContainer[FileCategory[ProcessedFile]] = container
        return value

    @staticmethod
    def _process_from_python_to_db(value: FileContainer) -> list[dict[str, Any]]:
        value: list[dict[str, Any]] = value.serializable()
        return value
