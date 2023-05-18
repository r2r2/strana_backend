from dataclasses import dataclass

from ajaximage.fields import AjaxImageField
from django.db import models
from django.forms import NumberInput
from django.db.models import Func
from django.db.models.fields import DecimalField, FloatField, IntegerField
from imagekit.processors import Thumbnail
from pilkit import utils

from .processors import Blur
from common.spec_fields import ImageSpecField
from .constants import PIXEL_RATIO, PREVIEW_RATIO, BLUR_RADIUS


utils.RGBA_TRANSPARENCY_FORMATS = ["PNG", "WEBP"]
JPEG_OPTS = {"progression": True, "optimize": True}
JPEG2k_OPTS = {"irreversible": True}
PNG_OPTS = {"optimize": True}


@dataclass
class Spec:
    source: str
    width: int = 0
    height: int = 0
    blur: int = False
    default: str = "jpeg"
    crop: bool = False


class MultiImageMeta(models.base.ModelBase):
    def __new__(mcs, name, bases, dct):
        if "image_map" not in dct:
            return super().__new__(mcs, name, bases, dct)
        for spec_name, spec in dct["image_map"].items():
            c = PREVIEW_RATIO if spec.blur else PIXEL_RATIO
            params = dict()
            if spec.width:
                params.update(dict(width=spec.width * c))
            if spec.height:
                params.update(dict(height=spec.height * c))
            processors = [Thumbnail(**params, crop=spec.crop, anchor="auto" if spec.crop else None)]
            if spec.blur:
                processors.append(Blur(BLUR_RADIUS))
            dct[f"{spec_name}_default"] = ImageSpecField(
                processors,
                format=spec.default.upper(),
                options=JPEG_OPTS if spec.default == "jpeg" else PNG_OPTS,
                source=spec.source,
            )
            dct[f"{spec_name}_webp"] = ImageSpecField(processors, "WEBP", JPEG_OPTS, spec.source)
        return super().__new__(mcs, name, bases, dct)


class FileMeta(MultiImageMeta):
    def __new__(mcs, name, bases, dct):
        dct["file"] = AjaxImageField("Файл", upload_to=dct["upload_to"])
        return super().__new__(mcs, name, bases, dct)


class File(models.Model, metaclass=FileMeta):
    upload_to = None

    class Meta:
        abstract = True


class OrderedFile(File):
    upload_to = None
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)

    class Meta:
        ordering = ["order"]
        abstract = True


class Image(models.Model, metaclass=FileMeta):
    upload_to = None

    class Meta:
        abstract = True


class OrderedImage(Image):
    upload_to = None
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)

    class Meta:
        ordering = ["order"]
        abstract = True


class Video(models.Model):
    url = models.URLField("Ссылка")

    class Meta:
        abstract = True


class OrderedVideo(Video):
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)

    class Meta:
        ordering = ["order"]
        abstract = True


class Page(models.Model):
    meta_title = models.CharField("Мета заголовок", max_length=200, blank=True)
    meta_description = models.TextField("Мета описание", blank=True)
    meta_keywords = models.TextField("Мета ключевые слова", blank=True)

    class Meta:
        abstract = True


class NumericOutputFieldMixin:

    # noinspection PyUnresolvedReferences,PyProtectedMember
    def _resolve_output_field(self):
        source_expressions = self.get_source_expressions()
        if any(isinstance(s.output_field, DecimalField) for s in source_expressions):
            return DecimalField()
        if any(isinstance(s.output_field, IntegerField) for s in source_expressions):
            return FloatField()
        return super()._resolve_output_field() if source_expressions else FloatField()


# noinspection PyAbstractClass
class Power(NumericOutputFieldMixin, Func):
    function = "POWER"
    arity = 2


class ActiveQuerySet(models.QuerySet):
    def filter_active(self):
        return self.filter(is_active=True)
