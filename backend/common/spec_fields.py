from django.core.files.storage import FileSystemStorage
from imagekit.models import ImageSpecField as BaseImageSpecField
from pilkit.processors import Thumbnail

from common.constants import (
    JPEG_QUALITY,
    PNG_QUALITY,
    PIXEL_RATIO,
    PREVIEW_RATIO,
    BLUR_RADIUS,
)
from common.processors import Blur

storage = FileSystemStorage()


class ImageSpecField(BaseImageSpecField):
    # noinspection PyUnresolvedReferences
    def contribute_to_class(self, cls, name):
        self._original_spec.options["name"] = name
        return super().contribute_to_class(cls, name)


class JpegImageSpecField(ImageSpecField):
    def __init__(
        self,
        processors=None,
        source=None,
        cachefile_storage=None,
        autoconvert=None,
        cachefile_backend=None,
        cachefile_strategy=None,
        spec=None,
        id=None,
    ):
        super().__init__(
            processors,
            "JPEG",
            {"progressive": True, "quality": JPEG_QUALITY},
            source,
            cachefile_storage,
            autoconvert,
            cachefile_backend,
            cachefile_strategy,
            spec,
            id,
        )


class WebPImageSpecField(ImageSpecField):
    def __init__(
        self,
        processors=None,
        source=None,
        cachefile_storage=None,
        autoconvert=None,
        cachefile_backend=None,
        cachefile_strategy=None,
        spec=None,
        id=None,
    ):
        super().__init__(
            processors,
            "WebP",
            {"minimize_size": True},
            source,
            cachefile_storage,
            autoconvert,
            cachefile_backend,
            cachefile_strategy,
            spec,
            id,
        )


class Jpeg2000ImageSpecField(ImageSpecField):
    def __init__(
        self,
        processors=None,
        source=None,
        cachefile_storage=None,
        autoconvert=None,
        cachefile_backend=None,
        cachefile_strategy=None,
        spec=None,
        id=None,
    ):
        super().__init__(
            processors,
            "JPEG2000",
            dict(quality_mode="dB", quality_layers=[41]),
            source,
            cachefile_storage,
            autoconvert,
            cachefile_backend,
            cachefile_strategy,
            spec,
            id,
        )


class PngImageSpecField(ImageSpecField):
    def __init__(
        self,
        processors=None,
        source=None,
        cachefile_storage=None,
        autoconvert=None,
        cachefile_backend=None,
        cachefile_strategy=None,
        spec=None,
        id=None,
    ):
        super().__init__(
            processors,
            "PNG",
            {"quality": PNG_QUALITY},
            source,
            cachefile_storage,
            autoconvert,
            cachefile_backend,
            cachefile_strategy,
            spec,
            id,
        )


class ThumbnailImageSpecField(JpegImageSpecField):
    def __init__(
        self,
        source=None,
        width=None,
        height=None,
        cachefile_storage=None,
        autoconvert=None,
        cachefile_backend=None,
        cachefile_strategy=None,
        spec=None,
        id=None,
        crop=True,
    ):
        super().__init__(
            [Thumbnail(int(width * PIXEL_RATIO), int(height * PIXEL_RATIO), crop=crop)],
            source,
            cachefile_storage,
            autoconvert,
            cachefile_backend,
            cachefile_strategy,
            spec,
            id,
        )


class ThumbnailWebPImageSpecField(WebPImageSpecField):
    def __init__(
        self,
        source=None,
        width=None,
        height=None,
        cachefile_storage=None,
        autoconvert=None,
        cachefile_backend=None,
        cachefile_strategy=None,
        spec=None,
        id=None,
        crop=True,
    ):
        super().__init__(
            [Thumbnail(int(width * PIXEL_RATIO), int(height * PIXEL_RATIO), crop=crop)],
            source,
            cachefile_storage,
            autoconvert,
            cachefile_backend,
            cachefile_strategy,
            spec,
            id,
        )


class ThumbnailJpeg2000ImageSpecField(Jpeg2000ImageSpecField):
    def __init__(
        self,
        source=None,
        width=None,
        height=None,
        cachefile_storage=None,
        autoconvert=None,
        cachefile_backend=None,
        cachefile_strategy=None,
        spec=None,
        id=None,
        crop=True,
    ):
        super().__init__(
            [Thumbnail(int(width * PIXEL_RATIO), int(height * PIXEL_RATIO), crop=crop)],
            source,
            cachefile_storage,
            autoconvert,
            cachefile_backend,
            cachefile_strategy,
            spec,
            id,
        )


class PreviewImageSpecField(JpegImageSpecField):
    def __init__(
        self,
        source=None,
        width=None,
        height=None,
        cachefile_storage=None,
        autoconvert=None,
        cachefile_backend=None,
        cachefile_strategy=None,
        spec=None,
        id=None,
    ):
        super().__init__(
            [
                Thumbnail(int(width * PREVIEW_RATIO), int(height * PREVIEW_RATIO), crop=True),
                Blur(BLUR_RADIUS),
            ],
            source,
            cachefile_storage,
            autoconvert,
            cachefile_backend,
            cachefile_strategy,
            spec,
            id,
        )


class PreviewWebPImageSpecField(WebPImageSpecField):
    def __init__(
        self,
        source=None,
        width=None,
        height=None,
        cachefile_storage=None,
        autoconvert=None,
        cachefile_backend=None,
        cachefile_strategy=None,
        spec=None,
        id=None,
    ):
        super().__init__(
            [
                Thumbnail(int(width * PREVIEW_RATIO), int(height * PREVIEW_RATIO), crop=True),
                Blur(BLUR_RADIUS),
            ],
            source,
            cachefile_storage,
            autoconvert,
            cachefile_backend,
            cachefile_strategy,
            spec,
            id,
        )


class PreviewJpeg2000ImageSpecField(Jpeg2000ImageSpecField):
    def __init__(
        self,
        source=None,
        width=None,
        height=None,
        cachefile_storage=None,
        autoconvert=None,
        cachefile_backend=None,
        cachefile_strategy=None,
        spec=None,
        id=None,
    ):
        super().__init__(
            [
                Thumbnail(int(width * PREVIEW_RATIO), int(height * PREVIEW_RATIO), crop=True),
                Blur(BLUR_RADIUS),
            ],
            source,
            cachefile_storage,
            autoconvert,
            cachefile_backend,
            cachefile_strategy,
            spec,
            id,
        )


class ThumbnailPngImageSpecField(PngImageSpecField):
    def __init__(
        self,
        source=None,
        width=None,
        height=None,
        cachefile_storage=None,
        autoconvert=None,
        cachefile_backend=None,
        cachefile_strategy=None,
        spec=None,
        id=None,
        crop=True,
    ):
        super().__init__(
            [Thumbnail(int(width * PIXEL_RATIO), int(height * PIXEL_RATIO), crop=crop)],
            source,
            cachefile_storage,
            autoconvert,
            cachefile_backend,
            cachefile_strategy,
            spec,
            id,
        )


class PreviewPngImageSpecField(PngImageSpecField):
    def __init__(
        self,
        source=None,
        width=None,
        height=None,
        cachefile_storage=None,
        autoconvert=None,
        cachefile_backend=None,
        cachefile_strategy=None,
        spec=None,
        id=None,
        crop=True,
    ):
        super().__init__(
            [
                Thumbnail(int(width * PREVIEW_RATIO), int(height * PREVIEW_RATIO), crop=crop),
                Blur(BLUR_RADIUS),
            ],
            source,
            cachefile_storage,
            autoconvert,
            cachefile_backend,
            cachefile_strategy,
            spec,
            id,
        )
