from solo.models import SingletonModel
from ckeditor.fields import RichTextField
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.conf import settings
from django.core.mail import send_mail

from amocrm.services import AmoCRM
from amocrm.models import AmoCRMManager
from amocrm.tasks import send_amocrm_lead
from common.utils import get_utm_data
from properties.constants import PropertyType
from . import logger
from .querysets import AuctionQuerySet, NotificationQuerySet


class Auction(models.Model):
    """Модель аукциона"""

    objects = AuctionQuerySet.as_manager()
    name = models.CharField("Название аукциона", max_length=128, blank=True)
    is_active = models.BooleanField("Активный", default=True)
    start_price = models.IntegerField("Стартовая цена", db_index=True, default=0)
    step = models.IntegerField("Шаг ставки", default=0)
    bet_count = models.IntegerField("Количество ставок", default=0)
    start = models.DateTimeField("Время начала аукциона", null=True, blank=True)
    end = models.DateTimeField("Время конца аукциона", null=True, blank=True)
    link = models.CharField("Ссылка аукциона", blank=True, max_length=300)
    property_object = models.ForeignKey(
        verbose_name="Объект собственности",
        to="properties.Property",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"type": PropertyType.COMMERCIAL},
    )

    def __str__(self):
        if self.start and self.end:
            return f'{self.start.strftime("%d.%m")}-{self.end.strftime("%d.%m")} {self.name}'
        return self.name

    class Meta:
        verbose_name = "Аукцион"
        verbose_name_plural = "Аукционы"


class Notification(models.Model):
    """Модель уведомления аукциона"""

    objects = NotificationQuerySet().as_manager()
    is_sent = models.BooleanField(verbose_name="Отправлено", default=False)
    name = models.CharField(verbose_name="Имя", blank=True, max_length=64)
    phone = PhoneNumberField(verbose_name="Телефон", null=True, blank=True)
    email = models.EmailField(verbose_name="Адрес электронной почты", blank=True)
    auction = models.ForeignKey(verbose_name="Аукцион", to=Auction, on_delete=models.CASCADE)
    lot_link = models.URLField(verbose_name="Ссылка лота", blank=True)

    class Meta:
        verbose_name = "Уведомление аукциона"
        verbose_name_plural = "Уведомления аукциона"

    def __str__(self):
        return f"Уведомление {self.pk}"

    def send_amocrm_lead(self, request) -> None:
        if settings.TESTING:
            return

        manager = AmoCRMManager.objects.filter(city__slug__contains="tyumen").first()
        if manager:
            send_amocrm_lead.delay(
                self.name,
                str(self.phone),
                description="Запрос на уведомление о начале аукциона",
                pipeline_status_id=manager.comm_pipeline_status_id,
                pipeline_id=manager.comm_pipeline_id,
                resp_user_id=manager.comm_crm_id,
                name_lead="Заявка с сайта",
                text=f"Запрос на уведомление о начале аукциона, отправлено с кнопки 'Уведомить' лота: {self.lot_link}",
                custom_fields=self._get_custom_fields(request),
            )
        else:
            logger.exception("Auction manager not found!")

    def _get_custom_fields(self, request):
        return AmoCRM.get_custom_fields(
            email=self.email,
            roistat_visit=request.COOKIES.get("roistat_visit"),
            smart_visitor_id=request.COOKIES.get("smart_visitor_id"),
            smart_session_id=request.COOKIES.get("smart_session_id"),
            utm_data=get_utm_data(request.COOKIES),
            metrika_cid=request.COOKIES.get("_ym_uid"),
            google_cid=(
                request.COOKIES.get("_ga")[6:] if request.COOKIES.get("_ga") is not None else ""
            ),
        )

    def notify_customer(self):
        send_mail(
            subject="Начало аукциона",
            message=f"{self.name.capitalize()}, наступила дата начала аукциона.\n Ссылка на лот: {self.lot_link}",
            from_email=settings.SERVER_EMAIL,
            recipient_list=[self.email],
        )

    def notify_manager(self):
        message = (
            f"Новый запрос на уведомление о начале аукциона, отправлено с кнопки 'Уведомить'.\n"
            f"Имя: {self.name},\nНомер: {self.phone},\nEmail: {self.email},\nЛот: {self.lot_link}"
        )
        send_mail(
            subject="Запрос на уведомление о начале аукциона",
            message=message,
            from_email=settings.SERVER_EMAIL,
            recipient_list=["oleg.stepanov@strana.com"],
        )


class AuctionRules(SingletonModel):
    stages = RichTextField("Этапы аукциона", null=True, blank=True)
    text = RichTextField("Текст правил")

    class Meta:
        verbose_name = "Правила аукциона"

    def __str__(self):
        return self._meta.verbose_name
