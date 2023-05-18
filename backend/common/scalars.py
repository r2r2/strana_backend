from graphene import String
from django.core.files.storage import default_storage

from common.storages import local_storage


class File(String):
    """Скалярный тип для FileField"""

    @staticmethod
    def serialize(value):
        """Сериализация файла в виде ссылки"""
        if not value:
            return ""
        if hasattr(value, "url"):
            return value.url
        return default_storage.url(value)


class LocalFile(String):
    """Скалярный тип для FileField"""

    @staticmethod
    def serialize(value):
        """Сериализация файла в виде ссылки"""
        if not value:
            return ""
        if hasattr(value, "url"):
            return value.url
        return local_storage.url(value)
