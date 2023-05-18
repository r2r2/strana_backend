from hmac import new
from textwrap import wrap
from hashlib import sha256
from base64 import urlsafe_b64encode
from typing import Union, Any, Optional

from django.conf import settings


class ImageProxy(object):
    """
    Imageproxy media builder
    """

    def __init__(
        self,
        source: str,
        enlarge: Optional[int] = 1,
        width: Optional[int] = 300,
        height: Optional[int] = 300,
        gravity: Optional[str] = "no",
        resize: Optional[str] = "fit",
    ):
        self._width: int = width
        self._resize: int = resize
        self._height: int = height
        self._gravity: str = gravity
        self._enlarge: int = enlarge
        self._s3_source: str = source

    def svg_to_png_url(self) -> Union[str, None]:
        result: str = None
        if self._s3_source[self._s3_source.rfind(".") + 1 :] == "svg":
            encoded_url: str = self._encode_url()
            path: str = self._build_path(encoded_url=encoded_url, extension="png")
            result: str = self._proxy_url(path=path)
        return result

    def _encode_url(self) -> str:
        url: bytes = bytes(self._s3_source.encode())
        encoded_url: str = "/".join(wrap(urlsafe_b64encode(url).rstrip(b"=").decode(), 16))
        return encoded_url

    def _build_path(self, encoded_url: str, extension: str) -> str:
        path: str = (
            "/{resize}/{width}/{height}/{gravity}/{enlarge}/{encoded_url}.{extension}"
        ).format(
            width=self._width,
            height=self._height,
            resize=self._resize,
            extension=extension,
            enlarge=self._enlarge,
            gravity=self._gravity,
            encoded_url=encoded_url,
        ).encode()
        return path

    def _proxy_url(self, path: str) -> str:
        key: bytes = bytes.fromhex(settings.IMGPROXY_KEY)
        salt: bytes = bytes.fromhex(settings.IMGPROXY_SALT)
        digest: Any = new(key, msg=salt + path, digestmod=sha256).digest()
        protection: str = urlsafe_b64encode(digest).rstrip(b"=")
        url: str = f"{protection}{path}".replace("b'", "").replace("'", "")
        proxy: str = f"https://{settings.IMGPROXY_SITE_HOST}/{url}"
        return proxy
