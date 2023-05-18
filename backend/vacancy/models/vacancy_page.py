from ajaximage.fields import AjaxImageField
from ckeditor.fields import RichTextField
from django.db import models
from solo.models import SingletonModel
from common.models import MultiImageMeta, Spec


class VacancyAbout(SingletonModel):
    """
    О компании
    """
    name = models.CharField(verbose_name='Название', max_length=200)
    desc = RichTextField(verbose_name='Описание', null=True, blank=True)
    img = models.ImageField(
        verbose_name='Изображение', upload_to="f/ip", null=True, blank=True
    )
    button_name = models.CharField(verbose_name='Название кнопки', max_length=200, null=True, blank=True)
    link = models.CharField(verbose_name='Ссылка', max_length=200, null=True, blank=True)
    form = models.ForeignKey(
        verbose_name="Форма",
        to="vacancy.VacancyPageForm",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'О компании'
        verbose_name_plural = 'О компании'

    def __str__(self):
        return self.name


class VacancyPageAdvantage(models.Model):
    """
    Преимущество на странице вакансий
    """

    title = models.CharField(verbose_name="Заголовок", max_length=200)
    icon = AjaxImageField(verbose_name="Иконка", upload_to="vacancy_page/icon", blank=True)

    page = models.ForeignKey(
        verbose_name="Страница вакансий", to=VacancyAbout, on_delete=models.CASCADE
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

    city = models.ForeignKey(
        "cities.City",
        verbose_name="Город",
        on_delete=models.CASCADE,
        related_name='employee_city',
        null=True,
        blank=True,
    )
    form = models.ForeignKey(
        "vacancy.VacancyPageForm", verbose_name="Форма", on_delete=models.PROTECT
    )
    full_name = models.CharField(verbose_name="ФИО", max_length=200)
    job_title = models.CharField(verbose_name="Должность", max_length=200, blank=True)
    image = AjaxImageField(
        verbose_name="Изображение",
        upload_to="f/i",
        null=True,
        blank=True,
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


class VacancyShouldWork(SingletonModel):
    """
    Почему вам стоит работать
    """
    name = models.CharField(verbose_name='Название', max_length=200)
    desc = RichTextField(verbose_name='Описание', null=True, blank=True)
    video = models.CharField(verbose_name='Видео', max_length=2000, null=True, blank=True)

    class Meta:
        verbose_name = 'Почему вам стоит работать'
        verbose_name_plural = 'Почему вам стоит работать'

    def __str__(self):
        return self.name


class VacancyShouldWorkSlider(models.Model):
    """
    Почему вам стоит работать ( слайдер )
    """

    name = models.CharField(verbose_name='Название категории', max_length=200)
    img = models.ImageField(
        verbose_name='Иконка', upload_to="f/ip", null=True, blank=True
    )
    desc = RichTextField(verbose_name='Текст при наведении на карточку', null=True, blank=True)

    order = models.PositiveIntegerField(verbose_name="Очередность", default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Почему вам стоит работать ( слайдер )"
        verbose_name_plural = "Почему вам стоит работать ( слайдер )"
        ordering = ("order",)


class VacancySlider(models.Model):
    """
    Слайдер ( кадры нашей жизни )
    """
    img = models.ImageField(
        verbose_name='Картинка', upload_to="f/ip"
    )

    class Meta:
        verbose_name = "Кадры нашей жизни"
        verbose_name_plural = "Кадры нашей жизни"


class VacancyEmployees(models.Model):
    """
    Сотрудники
    """
    fio = models.CharField(verbose_name='ФИО', max_length=200)
    title = models.CharField(verbose_name='Должность', max_length=200)
    desc = RichTextField(verbose_name='Описание', null=True, blank=True)
    img = models.ImageField(
        verbose_name='Иконка', upload_to="f/ip"
    )
    main_img = models.ImageField(
        verbose_name='Основное изображение', upload_to="f/ip"
    )
    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)

    def __str__(self):
        return self.fio

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ("order",)


class VacancyDescription(models.Model):
    title = models.CharField(verbose_name='Заголовок', max_length=200)
    desc = RichTextField(verbose_name='Описание')
    vacancy = models.ForeignKey(
        verbose_name='Вакансия', to="vacancy.Vacancy", on_delete=models.PROTECT
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Описание вакансии"
        verbose_name_plural = "Описания вакансии"
