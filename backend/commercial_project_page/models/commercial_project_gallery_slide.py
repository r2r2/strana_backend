from django.db import models
from ajaximage.fields import AjaxImageField
from common.models import MultiImageMeta, Spec


class CommercialProjectGallerySlide(models.Model, metaclass=MultiImageMeta):
    """
    Слайд галереи коммерческого проекта
    """

    WIDTH = 1440
    HEIGHT = 595

    title = models.CharField(verbose_name="Заголовок", max_length=100, null=True, blank=True)
    subtitle = models.CharField(verbose_name="Подзаголовок", max_length=300, null=True, blank=True)
    video = models.FileField(verbose_name="Видео (деск.)", blank=True, upload_to="cpp/pgs/v")
    video_mobile = models.FileField(verbose_name="Видео (моб.)", blank=True, upload_to="cpp/pgs/vm")

    image = AjaxImageField(
        verbose_name="Изображение",
        upload_to="p/gallery",
        blank=True,
        null=True,
        help_text=f"шир. - {WIDTH}, выс. - {HEIGHT}",
    )

    commercial_project_page = models.ForeignKey(
        verbose_name="Страница коммерческого проекта",
        to="commercial_project_page.CommercialProjectPage",
        on_delete=models.CASCADE,
        related_name="gallery_slides",
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)

    image_map = {
        "image_display": Spec(source="image", width=WIDTH, height=HEIGHT),
        "image_preview": Spec(source="image", width=WIDTH, height=HEIGHT, blur=True),
    }

    class Meta:
        verbose_name = "Слайд галереи"
        verbose_name_plural = "Слайды галереи"
        ordering = ("order",)

    def __str__(self):
        return f"{self._meta.verbose_name} #{self.order}"
