from django.db import models
from ajaximage.fields import AjaxImageField
from common.models import MultiImageMeta, Spec
from projects.models import Project


class ProjectGallerySlide(models.Model, metaclass=MultiImageMeta):
    """
    Слайд галереи
    """

    WIDTH_DESKTOP_BIG = 3200
    HEIGHT_DESKTOP_BIG = 1900
    WIDTH_DESKTOP_SMALL = 1830
    HEIGHT_DESKTOP_SMALL = 1168
    WIDTH_TABLET = 1152
    HEIGHT_TABLET = 811
    WIDTH_PHONE = 1280
    HEIGHT_PHONE = 1568

    title = models.CharField(verbose_name="Заголовок", max_length=100, null=True, blank=True)
    subtitle = models.CharField(verbose_name="Подзаголовок", max_length=300, null=True, blank=True)

    video = models.FileField(
        verbose_name="Видео (деск.)",
        blank=True, upload_to="p/pgs/v",
        help_text="шир. - 1920, выс. - 1080, размер - до 21 мб"
    )
    video_mobile = models.FileField(
        verbose_name="Видео (моб.)",
        blank=True, upload_to="p/pgs/vm",
        help_text="шир - 320, выс. - 500, размер - до 5 мб",
    )

    image = AjaxImageField(
        verbose_name="Изображение десктоп (большое)",
        upload_to="p/gallery",
        blank=True,
        null=True,
        help_text=f"шир. - {WIDTH_DESKTOP_BIG}, выс. - {HEIGHT_DESKTOP_BIG}, размер - до 1,5 мб",
    )

    image_desktop_small = models.ImageField(
        verbose_name="Изображение десктоп (маленькое)",
        upload_to="p/gallery/",
        null=True,
        blank=True,
        help_text=f"шир. - {WIDTH_DESKTOP_SMALL}, выс. - {HEIGHT_DESKTOP_SMALL}, размер - до 1 мб",

    )
    image_tablet = models.ImageField(
        verbose_name="Изображение планшет", upload_to="p/gallery", null=True, blank=True,
        help_text = f"шир. - {WIDTH_TABLET}, выс. - {HEIGHT_TABLET}, размер - до 750 кб",
    )
    image_phone = models.ImageField(
        verbose_name="Изображение телефон", upload_to="p/gallery", null=True, blank=True,
        help_text=f"шир. - {WIDTH_PHONE}, выс. - {HEIGHT_PHONE}, размер - до 430 кб",
    )

    project = models.ForeignKey(
        verbose_name="Проект", to=Project, on_delete=models.CASCADE, related_name="gallery_slides"
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)

    image_map = {
        "image_display": Spec(source="image", width=WIDTH_DESKTOP_BIG, height=HEIGHT_DESKTOP_BIG),
        "image_preview": Spec(source="image", width=WIDTH_DESKTOP_BIG, height=HEIGHT_DESKTOP_BIG, blur=True),
        "image_desktop_small_display": Spec(
            source="image_desktop_small", width=WIDTH_DESKTOP_SMALL, height=HEIGHT_DESKTOP_SMALL
        ),
        "image_desktop_small_preview": Spec(
            source="image_desktop_small",
            width=WIDTH_DESKTOP_SMALL,
            height=HEIGHT_DESKTOP_SMALL,
            blur=True,
        ),
        "image_tablet_display": Spec(
            source="image_tablet", width=WIDTH_TABLET, height=HEIGHT_TABLET
        ),
        "image_tablet_preview": Spec(
            source="image_tablet", width=WIDTH_TABLET, height=HEIGHT_TABLET, blur=True
        ),
        "image_phone_display": Spec(source="image_phone", width=WIDTH_PHONE, height=HEIGHT_PHONE),
        "image_phone_preview": Spec(
            source="image_phone", width=WIDTH_PHONE, height=HEIGHT_PHONE, blur=True
        ),
    }

    class Meta:
        verbose_name = "Слайд галереи"
        verbose_name_plural = "Слайды галереи"
        ordering = ("order",)

    def __str__(self):
        return f"{self._meta.verbose_name} #{self.order}"
