import pytz
from ajaximage.fields import AjaxImageField
from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.mail import send_mail
from django.db import models
from django.utils.html import mark_safe
from graphql_relay import to_global_id
from phonenumber_field.modelfields import PhoneNumberField

from amocrm.models import AmoCRMManager
from amocrm.services import AmoCRM
from amocrm.tasks import send_amocrm_lead
from app.settings import TESTING
from cities.models import City
from common.fields import ChoiceArrayField
from common.models import MultiImageMeta, Spec
from common.utils import get_utm_data
from properties.constants import ApplicantType, PropertyType
from vacancy.models.vacancy import Vacancy as NewVacancy

from .abstract import RequestBaseModel
from .classes import LK
from .constants import RequestType, TimeIntervalType

__all__ = [
    "SaleRequest",
    "SaleRequestDocument",
    "VacancyRequest",
    "CallbackRequest",
    "ExcursionRequest",
    "DirectorCommunicateRequest",
    "ReservationRequest",
    "NewsletterSubscription",
    "PurchaseHelpRequest",
    "CustomForm",
    "CustomRequest",
    "AgentRequest",
    "ContractorRequest",
    "ReservationLKRequest",
    "CustomFormEmployee",
    "CommercialRentRequest",
    "MediaRequest",
    "Manager",
    "LandingRequest",
    "TeaserRequest",
    "NewsRequest",
    "OfficeRequest",
    "LotCardRequest",
    "AntiCorruptionRequest",
    "FlatListingRequest",
    "FlatListingRequestForm",
    "StartSaleRequest",
    "PresentationRequest",
    "MallTeamRequest",
    "CommercialKotelnikiRequest",
    "BeFirstRequest",
    "AdvantageFormRequest",
    "ShowRequest",
    "StartProjectsRequest"
]


def get_property_type_list_default() -> list:
    return [t[0] for t in PropertyType.choices]


class Manager(models.Model):
    """
    Менеджер
    """

    name = models.CharField(verbose_name="Имя", max_length=200)
    email = models.EmailField(verbose_name="Email")
    is_active = models.BooleanField(verbose_name="Активный", default=True)

    type_list = ChoiceArrayField(
        verbose_name="Типы заявок",
        base_field=models.CharField(choices=RequestType.choices, max_length=20),
    )
    property_type_list = ChoiceArrayField(
        verbose_name="Типы недвижимости",
        help_text="Для отправки email-сообщений.",
        base_field=models.CharField(choices=PropertyType.choices, max_length=20),
        default=get_property_type_list_default,
    )
    cities = models.ManyToManyField(
        verbose_name="Города",
        to="cities.City",
        blank=True,
        help_text="Для отправки e-mail сообщений.",
    )

    def __str__(self) -> str:
        return self.email

    class Meta:
        verbose_name = "Менеджер"
        verbose_name_plural = "Менеджеры"


class SaleRequest(models.Model):
    """
    Заявка на продажу участка
    """

    name = models.CharField(verbose_name="Имя", max_length=200)
    phone = PhoneNumberField(verbose_name="Номер")
    email = models.EmailField("Email", max_length=200, null=True, blank=True)
    cadastral_number = models.CharField(verbose_name="Кадастровый номер", max_length=14)
    message = models.TextField(verbose_name="Сопроводительное письмо", blank=True)
    date = models.DateTimeField(verbose_name="Дата и время отправки", auto_now_add=True)

    price = models.DecimalField(
        verbose_name="Стоимость", max_digits=14, decimal_places=2, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} {self.cadastral_number}"

    class Meta:
        verbose_name = "Заявка на продажу участка"
        verbose_name_plural = "Заявки на продажу участка"
        ordering = ("-date",)


class SaleRequestDocument(models.Model):
    """
    Документ заявки на продажу участка
    """

    file = models.FileField(verbose_name="Файл", upload_to="requests/sale")

    request = models.ForeignKey(
        verbose_name="Заявка на продажу участка",
        to=SaleRequest,
        on_delete=models.CASCADE,
        related_name="document_set",
    )

    def __str__(self) -> str:
        return f"Документ {self.id}"

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"


class VacancyRequest(models.Model):
    """
    Отклик на вакансию
    """

    name = models.CharField(verbose_name="Имя", max_length=200)
    phone = PhoneNumberField(verbose_name="Номер")
    resume = models.FileField(verbose_name="Резюме", upload_to="request/vacancy", blank=True)
    message = models.TextField(verbose_name="Сопроводительное письмо", blank=True)
    date = models.DateTimeField(verbose_name="Дата и время отправки", auto_now_add=True)
    position = models.CharField(verbose_name="Должность", max_length=64, blank=True)
    city = models.CharField(verbose_name="Город", max_length=64, blank=True)
    graduated_at = models.DateField(verbose_name="Дата выпуска", blank=True, null=True)
    specialty = models.CharField(verbose_name="Специальность", blank=True, max_length=128)
    institution = models.CharField(verbose_name="Учебное заведение", blank=True, max_length=128)
    vacancy = models.ForeignKey(
        verbose_name="Вакансия", to=NewVacancy, on_delete=models.CASCADE, null=True, blank=True
    )

    category = models.ForeignKey(
        verbose_name="Категория",
        to="vacancy.VacancyCategory",
        on_delete=models.CASCADE,
        related_name='category_direction',
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"Отклик на вакансию {self.vacancy} от {self.date}"

    class Meta:
        verbose_name = "Отклик на вакансию"
        verbose_name_plural = "Отклики на вакансии"
        ordering = ("-date",)


class CallbackRequest(RequestBaseModel):
    """
    Заявка на обратный звонок
    """

    interval = models.CharField(
        verbose_name="Интервал для звонка",
        choices=TimeIntervalType.choices,
        default=TimeIntervalType.ANY,
        max_length=5,
    )
    amo_send = models.BooleanField(verbose_name="Заявка отправлена в АМО", default=True)
    site = models.ForeignKey(
        verbose_name="Сайт", to="sites.Site", null=True, blank=True, on_delete=models.SET_NULL
    )
    referer = models.URLField(null=True, blank=True)
    cookies = JSONField(null=True, blank=True)
    timezone_user = models.CharField(null=True, blank=True, max_length=25)

    class Meta:
        verbose_name = "Заявка на обратный звонок"
        verbose_name_plural = "Заявки на обратный звонок"
        ordering = ("-date",)

    def in_interval(self):
        if self.interval == TimeIntervalType.ANY:
            return True
        user_tz = self.timezone_user or settings.TIME_ZONE
        user_date = self.date.astimezone(pytz.timezone(user_tz))
        if user_date.hour in range(*[int(t) for t in self.interval.split("-")]):
            return True
        return False

    def format_text(self):
        msg = super().format_text()
        msg += f"Ссылка на страницу откуда пришла заявка:{self.referer}\n"
        return msg

    def get_current_site(self):
        if self.project:
            return self.project.city.site
        return self.site

    def get_city(self):
        try:
            return self.get_current_site().city
        except:
            return City.objects.first()

    def get_pipeline_ids(self):
        default_manager = AmoCRMManager.objects.default()
        assert default_manager, "Default manager is not set!"
        city = self.get_city()
        if self._check_tmn_commercial(city):
            resp_user_id = city.amocrmmanager.comm_crm_id
            pipeline_id = city.amocrmmanager.comm_pipeline_status_id
            pipeline_status_id = city.amocrmmanager.comm_pipeline_status_id
        else:
            resp_user_id = default_manager.crm_id
            pipeline_id = default_manager.pipeline_id
            pipeline_status_id = default_manager.pipeline_status_id
        return pipeline_id, pipeline_status_id, resp_user_id

    def send_amocrm_lead_without_http(self) -> None:
        if TESTING:
            return
        pipeline_id, pipeline_status_id, resp_user_id = self.get_pipeline_ids()

        send_amocrm_lead.delay(
            self.name,
            str(self.phone),
            description=self.get_description(),
            pipeline_status_id=pipeline_status_id,
            pipeline_id=pipeline_id,
            resp_user_id=resp_user_id,
            name_lead="Заявка с сайта",
            text=self.format_text(),
            custom_fields=self.get_custom_fields(),
        )
        self.amo_send = True
        self.save()

    def _check_tmn_commercial(self, city):
        return (
            city.short_name == "ТМН"
            and self.property_type == PropertyType.COMMERCIAL
            or self._meta.verbose_name == "Заявка на аренду коммерческого помещения"
        )

    def get_custom_fields(self) -> list:

        return AmoCRM.get_custom_fields(
            property_type=self.property_type,
            project_enum=self.project.amocrm_enum if self.project else None,
            project_name=self.project.amocrm_name if self.project else None,
            url_address=self.referer,
            city_name=self.get_city().short_name,
            roistat_visit=self.cookies.get("roistat_visit"),
            smart_visitor_id=self.cookies.get("smart_visitor_id"),
            smart_session_id=self.cookies.get("smart_session_id"),
            utm_data=get_utm_data(self.cookies),
            metrika_cid=self.cookies.get("_ym_uid"),
            google_cid=(self.cookies.get("_ga")[6:] if self.cookies.get("_ga") is not None else ""),
        )


class ReservationRequest(RequestBaseModel):
    """
    Заявка на бронирование
    """

    property = models.ForeignKey(
        "properties.Property", models.SET_NULL, blank=True, null=True, verbose_name="Помещение"
    )
    booking_type = models.ForeignKey(
        to="buildings.BuildingBookingType",
        verbose_name="Тип бронирования",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def format_text(self):
        text = super().format_text()
        if self.project:
            text += f" Проект: {self.project}"
        if self.property:
            text += f" Дом: {self.property.building}"
            text += f" Квартира: {self.property}"
            text += self.format_property_link()
        if self.booking_type:
            text += self.booking_type.__str__ + "\n"
        return text

    def format_property_link(self):
        if self.property_type == PropertyType.COMMERCIAL:
            property_path = "commercial"
            property_type = "GlobalCommercialSpaceType"
        else:
            property_path = "flats"
            property_type = "GlobalFlatType"
        current_site = self.get_current_site()
        property_ids = to_global_id(property_type, self.property.id)
        link = f" Ссылка - https://{current_site.domain}/{self.property.project.slug}/{property_path}/{property_ids}/"
        return link

    class Meta:
        verbose_name = "Заявка на бронирование"
        verbose_name_plural = "Заявки на бронирование"
        ordering = ("-date",)


class ReservationLKRequest(models.Model):
    """
    Заявка на бронирование в ЛК
    """

    date = models.DateTimeField(verbose_name="Дата и время отправки", auto_now_add=True)
    property_type = models.CharField(
        verbose_name="Тип", max_length=20, choices=PropertyType.choices
    )
    property = models.ForeignKey(
        verbose_name="Помещение",
        to="properties.Property",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    project = models.ForeignKey(
        verbose_name="Проект",
        to="projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def send_lk_lead(self) -> [bool, dict]:
        lk = LK(self)
        if TESTING:
            return True, lk.get_payload()
        response = lk.send_lead()
        return response.ok, lk.data

    class Meta:
        verbose_name = "Заявка на бронирование в ЛК"
        verbose_name_plural = "Заявки на бронирование в ЛК"
        ordering = ("-date",)


class ExcursionRequest(RequestBaseModel):
    """
    Запись на экскурсию
    """

    class Meta:
        verbose_name = "Запись на экскурсию"
        verbose_name_plural = "Записи на экскурсию"
        ordering = ("-date",)


class DirectorCommunicateRequest(RequestBaseModel):
    """
    Запрос на связь с директором
    """

    email = models.EmailField(verbose_name="Адрес электронной почты", blank=True)
    text = models.TextField(verbose_name="Сообщение")

    class Meta:
        verbose_name = "Запрос на связь с директором"
        verbose_name_plural = "Запросы на связь с директором"
        ordering = ("-date",)

    def format_text(self):
        msg = super().format_text()
        msg += f"Сообщение: {self.text}"
        return msg


class NewsletterSubscription(models.Model):
    """
    Подписка на рассылку
    """

    email = models.EmailField(verbose_name="Адрес электронной почты", unique=True, blank=True)
    date = models.DateTimeField(verbose_name="Дата и время подписки", auto_now_add=True)

    class Meta:
        verbose_name = "Подписка на рассылку"
        verbose_name_plural = "Подписки на рассылку"
        ordering = ("-date",)


class PurchaseHelpRequest(RequestBaseModel):
    """
    Заявка на помощь с оформлением покупки
    """

    class Meta:
        verbose_name = "Заявка на помощь с оформлением покупки"
        verbose_name_plural = "Заявки на помощь с оформлением покупки"
        ordering = ("-date",)


class AgentRequest(RequestBaseModel):
    """
    Заявка агенств
    """

    agency_name = models.CharField(
        verbose_name="Название агенства недвижимости", max_length=100, blank=True
    )
    city_name = models.CharField(verbose_name="Город", blank=True, max_length=64)

    class Meta:
        verbose_name = "Заявка агентств"
        verbose_name_plural = "Заявка агентств"
        ordering = ("-date",)


class ContractorRequest(RequestBaseModel):
    """
    Заявки для подрядчиков
    """

    type_of_job = models.CharField(verbose_name="Виды работ", blank=True, max_length=100)
    offer = models.FileField(
        verbose_name="Коммерческое предложение", upload_to="request/offer", blank=True
    )
    about_company = models.TextField(verbose_name="О компании подрядчика", blank=True)

    class Meta:
        verbose_name = "Заявки для подрядчиков"
        verbose_name_plural = "Заявки для подрядчиков"
        ordering = ("-date",)


class CommercialRentRequest(RequestBaseModel):
    """
    Заявки на аренду коммерческих помещений
    """

    class Meta:
        verbose_name = "Заявка на аренду коммерческого помещения"
        verbose_name_plural = "Заявки на аренду коммерческих помещений"
        ordering = ("-date",)


class MediaRequest(models.Model):
    """Заявка для СМИ"""

    name = models.CharField(verbose_name="Имя", max_length=200)
    phone = PhoneNumberField(verbose_name="Номер")
    email = models.EmailField("Email", max_length=200, null=True, blank=True)
    media_name = models.CharField(verbose_name="Назвиние СМИ", max_length=250, blank=True)
    comment = models.TextField("Комментарий", blank=True)
    date = models.DateTimeField(verbose_name="Дата и время отправки", auto_now_add=True)

    class Meta:
        ordering = ("-date",)
        verbose_name = "Заявка для СМИ"
        verbose_name_plural = "Заявки для СМИ"

    def __str__(self) -> str:
        return f"Заявка для СМИ от {self.date}"


class CustomForm(models.Model, metaclass=MultiImageMeta):
    """
    Кастомная форма
    """

    IMAGE_WIDTH = 1000
    IMAGE_HEIGHT = 906
    IMAGE_PHONE_WIDTH = 112
    IMAGE_PHONE_HEIGHT = 112

    name = models.CharField(verbose_name="Название", max_length=200)
    title = models.CharField(verbose_name="Заголовок", max_length=200, blank=True)
    description = RichTextField(verbose_name="Описание", blank=True)
    success = models.CharField(
        verbose_name="Сообщение при успешной отправке", max_length=200, blank=True
    )
    button_text = models.CharField(verbose_name="Текст на кнопке", max_length=200, blank=True)
    active = models.BooleanField(verbose_name="Активна", default=False)
    type_form = models.CharField("Тип для обработки запроса", blank=True, max_length=200)
    order = models.PositiveSmallIntegerField("Порядок", default=0)

    yandex_metrics = models.CharField(
        verbose_name="Яндекс метрика", max_length=100, null=True, blank=True
    )
    google_event_name = models.CharField("Название ивента Google", max_length=100, blank=True)
    full_name = models.CharField(verbose_name="ФИО", max_length=200, blank=True)
    job_title = models.CharField(verbose_name="Должность", max_length=200, blank=True)
    image = AjaxImageField(verbose_name="Изображение", upload_to="f/i", null=True, blank=True)
    image_phone = models.ImageField(
        verbose_name="Мобильное изображение", upload_to="f/ip", null=True, blank=True
    )

    image_map = {
        "image_display": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, False),
        "image_preview": Spec("image", IMAGE_WIDTH, IMAGE_HEIGHT, True),
        "image_phone_display": Spec("image_phone", IMAGE_PHONE_WIDTH, IMAGE_PHONE_HEIGHT, False),
        "image_phone_preview": Spec("image_phone", IMAGE_PHONE_WIDTH, IMAGE_PHONE_HEIGHT, True),
    }

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ("order",)
        verbose_name = "Форма кастомной заявки"
        verbose_name_plural = "Формы кастомных заявок"


class CustomRequest(RequestBaseModel):
    """
    Кастомная заявка
    """

    form = models.ForeignKey(
        verbose_name="Форма", to=CustomForm, on_delete=models.SET_NULL, null=True, blank=True
    )
    property = models.ForeignKey(
        verbose_name="Объект собственности",
        to="properties.Property",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Кастомная заявка"
        verbose_name_plural = "Кастомные заявки"
        ordering = ("-date",)


class CustomFormEmployee(models.Model, metaclass=MultiImageMeta):
    """Сотрудник на кастомой форме"""

    IMAGE_WIDTH = 1000
    IMAGE_HEIGHT = 906
    IMAGE_PHONE_WIDTH = 112
    IMAGE_PHONE_HEIGHT = 112

    city = models.ForeignKey(
        "cities.City", verbose_name="Город", on_delete=models.CASCADE, blank=True
    )
    project = models.ForeignKey(
        "projects.Project", verbose_name="Проект", on_delete=models.CASCADE, null=True, blank=True
    )
    form = models.ForeignKey(
        "request_forms.CustomForm", verbose_name="Форма", on_delete=models.PROTECT
    )
    is_for_comm_page = models.BooleanField("Показывать на странице коммерции", default=False)
    is_for_main_page = models.BooleanField("Показывать на главной странице", default=False)
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
        verbose_name = "Сотрудник на кастомой форме"
        verbose_name_plural = "Сотрудники кастомных форм"

    def __str__(self):
        return self.full_name


class LandingRequest(models.Model):
    """Модель заявки с лендинга"""

    name = models.CharField(verbose_name="Имя", max_length=32)
    phone = PhoneNumberField(verbose_name="Номер телефона", blank=True)
    email = models.EmailField(verbose_name="Почта", blank=True)
    block = models.ForeignKey(
        "landing.LandingBlock",
        verbose_name="Блок лендинга",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    landing = models.ForeignKey(
        "landing.Landing", verbose_name="Лендинг", on_delete=models.SET_NULL, blank=True, null=True
    )
    date = models.DateTimeField(verbose_name="Дата и время отправки", auto_now_add=True)

    class Meta:
        verbose_name = "Заявка с лендинга"
        verbose_name_plural = "Заявки с лендингов"
        ordering = ("-date",)

    def __str__(self) -> str:
        return f"Заявка с лендинга от {self.date}"

    def send_presentation(self):
        #if not self.block.send_to_email or not self.block.presentation:
        #    return

        send_mail(
            subject=f"Презентация со страницы '{self.block.landing.title}'",
            message=self.block.presentation.url,
            from_email=settings.SERVER_EMAIL,
            recipient_list=[self.email],
        )


class TeaserRequest(RequestBaseModel):
    """Заявка со слайда главной страницы"""

    related_object = models.ForeignKey(
        to="main_page.MainPageSlide",
        verbose_name="Слайд главной страницы",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("-date",)
        verbose_name = "Заявка со слайда главной страницы (тизера)"
        verbose_name_plural = "Заявки со слайдов главных страниц (тизеров)"

    def __str__(self) -> str:
        return f"Заявка со слайда главной страницы от {self.date}"

    def format_text(self):
        if not self.related_object:
            return super().format_text()
        text = f"Форма {self.related_object.form_title}.\n"
        text += f"Отправлено со слайда {mark_safe(self.related_object.title)}"
        return text


class AntiCorruptionRequest(models.Model):
    """Модель заявки о противодействии коррупции"""

    name = models.CharField(verbose_name="Имя", max_length=200)
    email = models.EmailField("Email", max_length=200, null=True, blank=True)
    message = models.TextField("Сообщение", blank=True)
    date = models.DateTimeField(verbose_name="Дата и время отправки", auto_now_add=True)

    class Meta:
        ordering = ("-date",)
        verbose_name = "Заявка о противодействии коррупции"
        verbose_name_plural = "Заявки о противодействии коррупции"

    def __str__(self):
        return f"Заявка о противодействии коррупции {self.date}"


class NewsRequest(RequestBaseModel):
    """Заявка со страницы новости"""

    related_object = models.ForeignKey(
        to="news.News", verbose_name="Новость", on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        ordering = ("-date",)
        verbose_name = "Заявка со страницы новости"
        verbose_name_plural = "Заявки со страницы новости"

    def __str__(self) -> str:
        return f"Заявка со страницы новости от {self.date}"

    def format_text(self):
        if not self.related_object:
            return super().format_text()
        text = f"Форма {self.related_object.form.title}.\n"
        text += f"Отправлено со страницы {self.related_object.get_url()}"
        return text


class OfficeRequest(RequestBaseModel):
    """Заявка на встречу в офисе"""

    related_object = models.ForeignKey(
        to="contacts.Office", verbose_name="Офис", on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        ordering = ("-date",)
        verbose_name = "Заявка на встречу в офисе"
        verbose_name_plural = "Заявки на встречу в офисе"

    def __str__(self) -> str:
        return f"Заявка записи на встречу в офисе от {self.date}"

    def format_text(self):
        text = super().format_text()
        if not self.related_object:
            return text
        text += f"Офис: {self.related_object.name}.\n"
        return text


class LotCardRequest(RequestBaseModel):
    """Заявка с карточки лота"""

    related_object = models.ForeignKey(
        to="properties.Property",
        verbose_name="Объект собственности",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    interval = models.CharField(verbose_name="Интервал обратной связи", blank=True, max_length=64)

    class Meta:
        ordering = ("-date",)
        verbose_name = "Заявка с карточки лота"
        verbose_name_plural = "Заявки с карточки лота"

    def __str__(self) -> str:
        return f"Заявка с карточки лота от {self.date}"

    def format_text(self):
        text = super().format_text()
        if not self.related_object:
            return text
        text += f"Лот: {self.related_object.get_url()}\nИнтервал обратной связи: {self.interval}"
        return text

    def get_description(self):
        return f"{self._meta.verbose_name}, желаемое время звонка {self.interval}"


class FlatListingRequestForm(models.Model):
    """Модель формы заявки в листинге квартир"""

    uptitle = models.CharField(verbose_name="Над заголовком", max_length=50, blank=True)
    name = models.CharField(verbose_name="Название", max_length=128)
    description = RichTextField(verbose_name="Описание", blank=True)
    button_name = models.CharField(verbose_name="Наименование кнопки", blank=True, max_length=128)

    class Meta:
        verbose_name = "Форма заявки в листинге квартир"
        verbose_name_plural = "Формы заявки в листинге квартир"

    def __str__(self):
        return self.name


class FlatListingRequest(RequestBaseModel):
    """Модель заявки в листинге квартир"""

    class Meta:
        verbose_name = "Заявка в листинге квартир"
        verbose_name_plural = "Заявки в листинге квартир"


class StartSaleRequest(models.Model):
    """Модель заявки на уведомление о старте продаж"""

    name = models.CharField(verbose_name="Имя", max_length=200)
    email = models.EmailField(verbose_name="Email", max_length=200)
    phone = PhoneNumberField(verbose_name="Номер", null=True, blank=True)
    project = models.ForeignKey(
        verbose_name="Проект", to="projects.Project", on_delete=models.CASCADE
    )
    property_type = models.CharField(
        verbose_name="Тип объекта собственности", max_length=20, choices=PropertyType.choices
    )
    date = models.DateTimeField(verbose_name="Дата и время отправки", auto_now_add=True)

    class Meta:
        ordering = ("-date",)
        verbose_name = "Заявка на уведомление о старте продаж"
        verbose_name_plural = "Заявки на уведомление о старте продаж"

    def __str__(self):
        return f"{self._meta.verbose_name} от {self.date}"

    @property
    def email_subject(self):
        return "Узнать о старте продаж"


class StartProjectsRequest(models.Model):
    """Модель откликов старта проекта"""

    name = models.CharField(verbose_name="Имя", max_length=200)
    email = models.EmailField(verbose_name="Email", max_length=200)
    phone = PhoneNumberField(verbose_name="Номер", null=True, blank=True)
    project = models.ForeignKey(
        verbose_name="Проект", to="projects.Project", on_delete=models.CASCADE
    )
    applicant = models.CharField(
        verbose_name="Тип заявителя", max_length=20, choices=ApplicantType.choices, default=ApplicantType.PERSON
    )
    date = models.DateTimeField(verbose_name="Дата и время отправки", auto_now_add=True)

    class Meta:
        ordering = ("-date",)
        verbose_name = "Отклики старта проекта"
        verbose_name_plural = "Отклики старта проекта"

    def __str__(self):
        return f"{self._meta.verbose_name} от {self.date}"

    @property
    def email_subject(self):
        return "Узнать о старте проекта"


class PresentationRequest(RequestBaseModel):
    name = None
    property_type = None

    class Meta:
        verbose_name = "Заявка на получение презентации"
        verbose_name_plural = "Заявки на получение презентации"


class MallTeamRequest(RequestBaseModel):
    property_type = None

    class Meta:
        verbose_name = "Заявка с формы MallTeam"
        verbose_name_plural = "Заявки с формы MallTeam"


class CommercialKotelnikiRequest(models.Model):
    """Заявка коммерции Котельники"""

    name = models.CharField(verbose_name="Имя", max_length=200)
    phone = PhoneNumberField(verbose_name="Номер")
    from_url = models.URLField(verbose_name="Отправлено со страницы")
    date = models.DateTimeField(verbose_name="Дата и время отправки", auto_now_add=True)

    class Meta:
        verbose_name = "Заявка коммерции Котельники"
        verbose_name_plural = "Заявки коммерции Котельники"

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} от {self.date}"


class BeFirstRequest(models.Model):
    """Заявка 'Узнайте о новых проектах'"""

    email = models.EmailField("E-mail")
    date = models.DateTimeField("Дата отправки", auto_now_add=True)
    subdomain = models.CharField("Поддомен", max_length=20)

    class Meta:
        verbose_name = "Заявка 'Узнайте о новых проектах'"
        verbose_name_plural = "Заявки 'Узнайте о новых проектах'"


class AdvantageFormRequest(RequestBaseModel):
    name = None

    class Meta:
        verbose_name = "Заявка с формы УТП"
        verbose_name_plural = "Заявки с формы УТП"


class ShowRequest(RequestBaseModel):
    """Модель заявки записи на показ"""

    class Meta:
        verbose_name = "Заявка записи на показ"
        verbose_name_plural = "Заявки записи на показ"


class EKBStartSaleRequest(models.Model):
    """Модель заявки на уведомление о старте продаж в Екатеринбурге """
    name = models.CharField(verbose_name="Имя", max_length=1024, blank=True, default="")
    email = models.EmailField(verbose_name="Email", max_length=200)
    phone = PhoneNumberField(verbose_name="Номер", null=True, blank=True)
    applicant = models.CharField(
        verbose_name="Тип заявителя", max_length=20, choices=ApplicantType.choices, default=ApplicantType.PERSON
    )
    date = models.DateTimeField(verbose_name="Дата и время отправки", auto_now_add=True)

    class Meta:
        ordering = ("-date",)
        verbose_name = "Заявка на уведомление о старте продаж"
        verbose_name_plural = "Заявки на уведомление о старте продаж"

    def __str__(self):
        return f"{self._meta.verbose_name} от {self.date}"

    @property
    def email_subject(self):
        return "Узнать о старте продаж"
