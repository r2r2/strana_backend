import os
from tempfile import SpooledTemporaryFile
from storages.backends.s3boto3 import S3Boto3Storage
from django_hashedfilenamestorage.storage import (
    HashedFilenameMetaStorage,
    HashedFilenameFileSystemStorage,
)


class CustomS3Boto3Storage(S3Boto3Storage):
    def _save(self, obj, content):
        content.seek(0, os.SEEK_SET)
        content_autoclose = SpooledTemporaryFile()
        content_autoclose.write(content.read())
        res = super(CustomS3Boto3Storage, self)._save(obj, content_autoclose)
        if not content_autoclose.closed:
            content_autoclose.close()

        return res


HashedFilenameS3Boto3Storage = HashedFilenameMetaStorage(storage_class=CustomS3Boto3Storage)

local_storage = HashedFilenameFileSystemStorage()
