# pylint: disable=no-member,invalid-str-returned
from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField


class Caution(models.Model):
    """
    Модель предупреждения, выводимого пользователю
    """

    # TODO : предлагаю вынести CautionType из кабинета constants.py
    class CautionType(models.TextChoices):
        """
        Тип предупреждения
        """
        INFORMATION = "information", _("Информация")
        WARNING = "warning", _("Предупреждение")

    is_active = models.BooleanField(
        verbose_name="Активность", default=False, help_text="Неактивные предупреждения не выводятся на сайте"
    )
    type = models.CharField(
        choices=CautionType.choices,
        default=CautionType.INFORMATION,
        max_length=20,
        verbose_name='Тип',
        help_text="Определяет внешний вид выводимого предупреждения",
    )
    roles = models.JSONField(
        null=True,
        blank=True,
        default=list,
        verbose_name="Доступно ролям",
        help_text="Предупреждение будет выводиться всем пользователям с указанными ролями"
    )
    text = models.TextField(verbose_name="Выводимый текст", help_text="HTML-теги недопустимы")
    priority = models.SmallIntegerField(
        verbose_name="Приоритет",
        help_text="Чем ниже приоритет, тем выше будет выводиться предупреждение",
    )
    expires_at = models.DateTimeField(verbose_name="Активен до", help_text="Когда будет деактивировано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано", help_text="Дата создания")
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True,
        verbose_name="Обновлено",
        help_text="Дата последнего обновления"
    )
    created_by = models.ForeignKey(
        "users.CabinetUser",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="cautions_created",
        verbose_name="Кем создано",
        help_text="Кем создано"
    )
    update_by = models.ForeignKey(
        "users.CabinetUser",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="cautions_updated",
        verbose_name="Кем обновлено",
        help_text="Кем обновлено"
    )

    def __str__(self) -> str:
        if self.type:
            type_value = str(self.CautionType._value2label_map_.get(self.type))
            return type_value
        return self.type

    class Meta:
        managed = False
        db_table = "cautions_caution"
        verbose_name = "Предупреждение"
        verbose_name_plural = "5.1. [ЛК Брокера] Баннер предупреждений"
        ordering = ["priority"]


class CautionMute(models.Model):
    """
    Модель связи тех, кого уже уведомили предупреждением
    """

    user = models.ForeignKey(
        "users.CabinetUser",
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Пользователь"
    )
    caution = models.ForeignKey(
        "contents.Caution",
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Предупреждение"
    )

    class Meta:
        managed = False
        db_table = "users_caution_mute"
        verbose_name = "Уведомление пользователя"
        verbose_name_plural = "Уведомления пользователей"


class LkType(models.TextChoices):
    BROKER: str = "lk_broker", "ЛК Брокера"
    CLIENT: str = "lk_client", "ЛК Клиента"


class TextBlock(models.Model):
    """
    Текстовые блоки.
    """

    title = models.TextField(
        verbose_name="Заголовок блока",
        null=True,
        blank=True,
        help_text="H1 заголовок страницы / слайд-панели",
    )
    text = RichTextField(
        verbose_name="Текст блока",
        null=True,
        blank=True,
    )
    slug = models.CharField(
        max_length=100,
        verbose_name="Слаг текстового блока",
        help_text="Максимум 100 символов, для привязки к событию на беке",
        unique=True,
    )
    lk_type: str = models.CharField(
        verbose_name="Сервис ЛК, в котором применяется текстовый блок",
        choices=LkType.choices,
        max_length=10,
        help_text="Не участвует в бизнес-логике, поле для фильтрации в админке",
    )
    description = models.TextField(
        verbose_name="Описание назначения текстового блока",
        null=True,
        blank=True,
        help_text="Не участвует в бизнес-логике, поле для доп. описания",
    )

    created_at = models.DateTimeField(verbose_name="Когда создано", help_text="Когда создано", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Когда обновлено", help_text="Когда обновлено", auto_now=True)

    def __str__(self) -> str:
        return self.slug

    class Meta:
        db_table = "text_block_text_block"
        verbose_name = "Текстовый блок"
        verbose_name_plural = "5.3. [ЛК Брокера] Текстовые блоки"


class BrokerRegistration(models.Model):
    """
    Регистрация брокера
    """

    new_pwd_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/br/i")
    login_pwd_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/br/i")
    forgot_pwd_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/br/i")
    forgot_send_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/br/i")
    login_email_image = models.ImageField(max_length=500, blank=True, null=True, upload_to="p/br/i")
    enter_agency_image = models.ImageField(
        max_length=500, blank=True, null=True, upload_to="p/br/i"
    )
    confirm_send_image = models.ImageField(
        max_length=500, blank=True, null=True, upload_to="p/br/i"
    )
    enter_personal_image = models.ImageField(
        max_length=500, blank=True, null=True, upload_to="p/br/i"
    )
    enter_password_image = models.ImageField(
        max_length=500, blank=True, null=True, upload_to="p/br/i"
    )
    accept_contract_image = models.ImageField(
        max_length=500, blank=True, null=True, upload_to="p/br/i"
    )
    confirmed_email_image = models.ImageField(
        max_length=500, blank=True, null=True, upload_to="p/br/i"
    )

    def __str__(self) -> str:
        return self._meta.verbose_name

    class Meta:
        managed = False
        db_table = "pages_broker_registration"
        verbose_name = "Регистрация брокера"
        verbose_name_plural = "5.2. [ЛК Брокера] Изображение при регистрации"


class Instruction(models.Model):
    """
    Инструкции.
    """

    slug = models.CharField(
        max_length=50,
        verbose_name="Слаг инструкции",
    )
    link_text = models.TextField(
        verbose_name="Текст ссылки",
    )
    file = models.FileField(
        verbose_name="Файл инструкции",
        max_length=500,
        upload_to="d/i/f",
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return self.slug

    class Meta:
        managed = False
        db_table = "documents_instruction"
        verbose_name = "Инструкция"
        verbose_name_plural = "5.4. Инструкции пользователя"

# class MortgageTextBlock(models.Model):
#     """
#     Текстовые блоки для ик.
#     """

#     title = models.TextField(
#         verbose_name="Заголовок блока",
#         null=True,
#         blank=True,
#         help_text="H1 заголовок страницы / слайд-панели",
#     )
#     text = RichTextField(
#         verbose_name="Текст блока",
#         null=True,
#         blank=True,
#     )
#     slug = models.CharField(
#         max_length=100,
#         verbose_name="Слаг текстового блока",
#         help_text="Максимум 100 символов, для привязки к событию на беке",
#         unique=True,
#     )
#     lk_type: str = models.CharField(
#         verbose_name="Сервис ЛК, в котором применяется текстовый блок",
#         choices=LkType.choices,
#         max_length=10,
#         help_text="Не участвует в бизнес-логике, поле для фильтрации в админке",
#     )
#     description = models.TextField(
#         verbose_name="Описание назначения текстового блока",
#         null=True,
#         blank=True,
#         help_text="Не участвует в бизнес-логике, поле для доп. описания",
#     )

#     created_at = models.DateTimeField(verbose_name="Когда создано", help_text="Когда создано", auto_now_add=True)
#     updated_at = models.DateTimeField(verbose_name="Когда обновлено", help_text="Когда обновлено", auto_now=True)

#     def __str__(self) -> str:
#         return self.slug

#     class Meta:
#         db_table = "text_block_text_block"
#         verbose_name = "Текстовый блок для ик"
#         verbose_name_plural = "5.6. [ЛК Клиента] Текстовые блоки"
