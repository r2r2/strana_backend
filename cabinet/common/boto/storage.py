from functools import partial
from typing import Any, Union, Optional, Generator

from aioboto3.session import Session
from botocore.exceptions import ClientError, DataNotFoundError

from config import aws_config


class BotoStorage(object):
    """
    Boto storage
    """

    def __init__(self):
        self.service_name: str = "s3"
        self.endpoint_url: str = aws_config["endpoint_url"]
        self.bucket: str = aws_config["storage_bucket_name"]
        self.aws_access_key_id: str = aws_config["access_key_id"]
        self.aws_secret_access_key: str = aws_config["secret_access_key"]

        self.session_options: dict[str, Any] = dict(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )
        self.client_options: dict[str, Any] = dict(
            service_name=self.service_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )
        self.resource_options: dict[str, Any] = dict(
            service_name=self.service_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

        self.session: Session = Session(**self.session_options)

    async def stream_file(
        self, source: str, chunk_size: Optional[int] = 4096
    ) -> Generator[bytes, None, None]:
        prefix: str = "/".join(source.split("/")[:-1])
        async with self.session.resource(**self.resource_options) as s3:
            bucket = await s3.Bucket(self.bucket)
            async for obj in bucket.objects.filter(Prefix=prefix):
                if obj.key == source:
                    try:
                        s3_ob = await obj.get()
                        async with s3_ob["Body"] as stream:
                            stream_read = (
                                partial(stream.read, chunk_size) if chunk_size else stream.read
                            )
                            chunk = await stream_read()
                            while chunk:
                                yield chunk
                                chunk = await stream_read()
                    except ClientError as e:
                        if e.response["Error"]["Code"] == "NoSuchKey":
                            raise DataNotFoundError
                        else:
                            raise e
                    return
        raise DataNotFoundError

    async def upload_file(self, file: Any, source: str) -> Union[str, None]:
        await file.seek(0)
        async with self.session.client(**self.client_options) as s3:
            await s3.upload_fileobj(file, self.bucket, source)
        return source

    async def delete_file(self, source: str) -> Union[str, None]:
        prefix: str = "/".join(source.split("/")[:-1])
        async with self.session.resource(**self.resource_options) as s3:
            bucket = await s3.Bucket(self.bucket)
            async for obj in bucket.objects.filter(Prefix=prefix):
                if obj.key == source:
                    await obj.delete()
        return source
