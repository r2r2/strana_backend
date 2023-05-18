from fastapi import UploadFile
from typing import Iterable

from common.mixins import ExceptionMixin
from common.utils import get_mimetype


class UploadedFileValidation(ExceptionMixin):

    def check_file_size(self,
                        uploaded_file: UploadFile,
                        max_size_bytes: int,
                        *,
                        raise_exception: bool = False
                        ) -> bool:
        """Проверка размера файла"""

        file_bytes = uploaded_file.file.read()
        result = file_bytes.__sizeof__() <= max_size_bytes
        if not result and raise_exception:
            raise self.exception_class(
                f'{uploaded_file.filename}: Максимальный размер файла: {max_size_bytes / 1024 ** 2:.2f}Mb'
            )
        uploaded_file.file.seek(0)
        return result

    def check_file_type(self,
                        uploaded_file: UploadFile,
                        allowed_extensions: Iterable,
                        *,
                        raise_exception: bool = False
                        ) -> bool:
        """Проверка типа файла"""

        file_mimetype = get_mimetype(uploaded_file.filename)
        result = file_mimetype in allowed_extensions
        if not result and raise_exception:
            raise self.exception_class(
                f'{uploaded_file.filename}: Принимаются только файлы с расширениями: {allowed_extensions}'
            )
        return file_mimetype in allowed_extensions
