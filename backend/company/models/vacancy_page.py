from ajaximage.fields import AjaxImageField
from ckeditor.fields import RichTextField
from django.db import models
from solo.models import SingletonModel
from common.models import MultiImageMeta, Spec


class VacancyPage(SingletonModel):
    """
    Страница вакансий
    """

    text_1 = RichTextField(verbose_name="Описание 1", null=True, blank=True)
    text_2 = RichTextField(verbose_name="Описание 2", null=True, blank=True)

    advantages_title_1 = models.CharField(
        verbose_name="Преимущества / Заголовок 1", max_length=200, blank=True
    )
    advantages_title_2 = models.CharField(
        verbose_name="Преимущества / Заголовок 2", max_length=200, blank=True
    )
    advantages_button_text_1 = models.CharField(
        verbose_name="Преимущества / Текст кнопки 1", max_length=100, blank=True
    )
    advantages_button_text_2 = models.CharField(
        verbose_name="Преимущества / Текст кнопки 2", max_length=100, blank=True
    )

    video = models.CharField(verbose_name="Видео", max_length=2000, blank=True)
    video_preview = AjaxImageField(verbose_name="Видео / Превью", null=True, blank=True)
    video_title = models.CharField(verbose_name="Видео / Заголовок", max_length=200, blank=True)
    video_description = models.TextField(verbose_name="Видео / Описание", blank=True)
    vacancies = models.CharField(verbose_name="Вакансии", max_length=30, null=True, blank=True)
    vacancies_description = RichTextField(
        verbose_name="Описание вакансий", max_length=1000, null=True, blank=True
    )
    form = models.ForeignKey(
        verbose_name="Форма",
        to="company.VacancyPageForm",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self._meta.verbose_name

    class Meta:
        verbose_name = "Страница вакансий"
        verbose_name_plural = "Страница вакансий"


class VacancyPageAdvantage(models.Model):
    """
    Преимущество на странице вакансий
    """

    title = models.CharField(verbose_name="Заголовок", max_length=200)
    icon = AjaxImageField(verbose_name="Иконка", upload_to="vacancy_page/icon", blank=True)

    page = models.ForeignKey(
        verbose_name="Страница вакансий", to=VacancyPage, on_delete=models.CASCADE
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Преимущество вакансий"
        verbose_name_plural = "Преимущества вакансий"
        ordering = ("order",)


class VacancyPageForm(models.Model, metaclass=MultiImageMeta):
    """
    Форма на странице вакансий
    """

    IMAGE_WIDTH = 500
    IMAGE_HEIGHT = 453
    IMAGE_PHONE_WIDTH = 56
    IMAGE_PHONE_HEIGHT = 56

    name = models.CharField(verbose_name="Название", max_length=200, blank=True)
    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    description = RichTextField(verbose_name="Описание", blank=True)

    image = AjaxImageField(
        verbose_name="Изображение",
        upload_to="f/i",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    image_phone = models.ImageField(
        verbose_name="Изображение телефон", upload_to="f/ip", null=True, blank=True
    )

    button_text = models.CharField(verbose_name="Текст на кнопке", max_length=200, blank=True)
    full_name = models.CharField(verbose_name="ФИО", max_length=200, blank=True)
    job_title = models.CharField(verbose_name="Должность", max_length=200, blank=True)
    yandex_metrics = models.CharField(
        verbose_name="Яндекс метрика", max_length=100, null=True, blank=True
    )
    google_event_name = models.CharField("Название ивента Google", max_length=100, blank=True)

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "image_phone_display": Spec("image_phone", IMAGE_PHONE_WIDTH, IMAGE_PHONE_HEIGHT, False),
        "image_phone_preview": Spec("image_phone", IMAGE_PHONE_WIDTH, IMAGE_PHONE_HEIGHT, True),
    }

    def __str__(self) -> str:
        return f"{self.id} - {self.full_name}"

    class Meta:
        verbose_name = "Форма на странице вакансий"
        verbose_name_plural = "Формы на странице вакансий"


class VacancyPageFormEmployee(models.Model, metaclass=MultiImageMeta):
    """ Сотрудник формы страницы вакансий """

    IMAGE_WIDTH = 1000
    IMAGE_HEIGHT = 906
    IMAGE_PHONE_WIDTH = 112
    IMAGE_PHONE_HEIGHT = 112

    city = models.ForeignKey("cities.City", verbose_name="Город", on_delete=models.CASCADE)
    form = models.ForeignKey(
        "company.VacancyPageForm", verbose_name="Форма", on_delete=models.PROTECT
    )
    full_name = models.CharField(verbose_name="ФИО", max_length=200)
    job_title = models.CharField(verbose_name="Должность", max_length=200, blank=True)
    image = AjaxImageField(
        verbose_name="Изображение",
        upload_to="f/i",
        null=True,
        blank=True,
        help_text=f"шир. - {IMAGE_WIDTH}, выс. - {IMAGE_HEIGHT}",
    )
    image_phone = models.ImageField(
        verbose_name="Мобильное изображение", upload_to="f/ip", null=True, blank=True
    )

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "image_phone_display": Spec("image_phone", IMAGE_PHONE_WIDTH, IMAGE_PHONE_HEIGHT, False),
        "image_phone_preview": Spec("image_phone", IMAGE_PHONE_WIDTH, IMAGE_PHONE_HEIGHT, True),
    }

    class Meta:
        verbose_name = "Сотрудник формы страницы вакансий"
        verbose_name_plural = "Сотрудники формы страницы вакансий"

    def __str__(self):
        return self.full_name
