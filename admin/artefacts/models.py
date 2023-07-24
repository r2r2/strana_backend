from django.db import models
from ckeditor.fields import RichTextField


class CheckUnique(models.Model):
    """
    Проверка на уникальность
    """

    check_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/cu/i")
    result_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/cu/i")

    def __str__(self) -> str:
        return self._meta.verbose_name

    class Meta:
        managed = False
        db_table = "pages_check_unique"
        verbose_name = "Проверка на уникальность"
        verbose_name_plural = "15.6. Проверка на уникальность"


class ShowtimeRegistration(models.Model):
    """
    Запись на показ
    """

    result_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/sr/i")

    def __str__(self) -> str:
        return self._meta.verbose_name

    class Meta:
        managed = False
        db_table = "pages_showtime_registration"
        verbose_name = "Запись на показ"
        verbose_name_plural = "15.5. Запись на показ"


class Document(models.Model):
    """
    Документ
    """

    text = RichTextField()
    slug = models.CharField(max_length=50)
    file = models.FileField(max_length=500, blank=True, null=True, upload_to="d/d/f")

    def __str__(self) -> str:
        return self.slug

    class Meta:
        managed = False
        db_table = "documents_document"
        verbose_name = "Документ"
        verbose_name_plural = "15.2. Документы"


class Escrow(models.Model):
    """
    Памятка Эскроу
    """

    slug = models.CharField(max_length=50)
    file = models.FileField(max_length=500, blank=True, null=True, upload_to="d/d/f")

    def __str__(self) -> str:
        return self.slug

    @property
    def file_url(self):
        return self.file.url

    class Meta:
        managed = False
        db_table = "documents_escrow"
        verbose_name = "Памятка Эскроу"
        verbose_name_plural = "15.3. Памятки Эскроу"


class BookingHelpText(models.Model):
    class OnlinePurchaseSteps(models.TextChoices):
        ONLINE_PURCHASE_START = "online_purchase_start", "Начало онлайн покупки"
        PAYMENT_METHOD_SELECT = "payment_method_select", "Выбор способа покупки"
        AMOCRM_AGENT_DATA_VALIDATION = (
            "amocrm_agent_data_validation",
            "Ожидайте, введённые данные на проверке",
        )
        DDU_CREATE = "ddu_create", "Оформление договора"
        AMOCRM_DDU_UPLOADING_BY_LAWYER = (
            "amocrm_ddu_uploading_by_lawyer",
            "Ожидание загрузки ДДУ юристом",
        )
        DDU_ACCEPT = "ddu_accept", "Согласование договора"
        ESCROW_UPLOAD = "escrow_upload", "Загрузка эскроу-счёта"
        AMOCRM_SIGNING_DATE = (
            "amocrm_signing_date",
            "Ожидание назначения даты подписания договора",
        )
        AMOCRM_SIGNING = "amocrm_signing", "Ожидание подписания договора"
        FINISHED = "finished", "Зарегистрировано"

    class PaymentMethods(models.TextChoices):
        CASH = "cash", "Наличные"
        MORTGAGE = "mortgage", "Ипотека"
        INSTALLMENT_PLAN = "installment_plan", "Рассрочка"

    text = models.TextField(verbose_name="Текст")
    booking_online_purchase_step = models.CharField(
        verbose_name="Стадия онлайн-покупки", max_length=50, choices=OnlinePurchaseSteps.choices
    )
    payment_method = models.CharField(
        verbose_name="Тип покупки", max_length=20, choices=PaymentMethods.choices
    )
    maternal_capital = models.BooleanField(verbose_name="Мат. капитал")
    certificate = models.BooleanField(verbose_name="Жил. сертификат")
    loan = models.BooleanField(verbose_name="Гос. займ")
    default = models.BooleanField(verbose_name="Текст по-умолчанию", default=False)

    class Meta:
        managed = False
        db_table = "booking_purchase_help_text"
        verbose_name = 'Текст для страницы "Как купить онлайн?"'
        verbose_name_plural = '15.1. Тексты для страницы "Как купить онлайн?"'
        ordering = [
            "default",
            "booking_online_purchase_step",
            "payment_method",
            "id",
        ]


class Tip(models.Model):
    """
    Подсказка
    """

    image = models.ImageField(max_length=500, blank=True, null=True, upload_to="t/t/i")
    title = models.CharField(max_length=200, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "tips_tip"
        verbose_name = "Подсказка"
        verbose_name_plural = "15.4. Подсказки"
        ordering = ("order",)
