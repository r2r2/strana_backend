# pylint: disable=no-member
from django.db import models


class BookingTag(models.Model):
    """
    Тег сделки
    """
    class BookingTagStyle(models.TextChoices):
        """
        Стили тегов
        """
        PRIMARY: str = "primary", "Основной"
        SECONDARY: str = "secondary", "Второстепенный"
        DANGER: str = "danger", "Опасный"
        WARNING: str = "warning", "Предупреждение"
        INFO: str = "info", "Информация"
        LIGHT: str = "light", "Светлый"
        DARK: str = "dark", "Темный"
        LINK: str = "link", "Ссылка"
        DEFAULT: str = "default", "По умолчанию"
        SUCCESS: str = "success", "Успешно"
        WHITE: str = "white", "Белый"
        TRANSPARENT: str = "transparent", "Прозрачный"

    label: str = models.CharField(max_length=100, verbose_name='Название')
    style: str = models.CharField(
        max_length=20,
        verbose_name='Стиль',
        choices=BookingTagStyle.choices,
    )
    slug: str = models.CharField(max_length=255, verbose_name='Слаг тега')
    priority: int = models.IntegerField(
        verbose_name='Приоритет',
        help_text='Чем меньше приоритет - тем выше выводится тег в списке',
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name="Активность", default=False, help_text="Неактивные теги не выводятся на сайте"
    )
    group_status = models.ManyToManyField(
        blank=True,
        verbose_name="Групповые статусы по тегам",
        to="booking.AmocrmGroupStatus",
        through="GroupStatusTagThrough",
        through_fields=("tag", "group_status"),
        related_name="booking_tags",
    )

    client_group_status = models.ManyToManyField(
        blank=True,
        verbose_name="Групповые статусы клиентов по тегам",
        to="booking.ClientAmocrmGroupStatus",
        through="ClientGroupStatusTagThrough",
        through_fields=("tag", "client_group_status"),
        related_name="booking_tags",
    )

    def __str__(self):
        return self.label

    class Meta:
        managed = False
        db_table = 'booking_bookingtag'
        verbose_name = "Тег сделки: "
        verbose_name_plural = " 1.9. [Справочник] Теги сделок"


class GroupStatusTagThrough(models.Model):
    group_status = models.OneToOneField(
        verbose_name="Статус",
        to="booking.AmocrmGroupStatus",
        on_delete=models.CASCADE,
        related_name="booking_tag_through",
        primary_key=True,
    )
    tag = models.ForeignKey(
        verbose_name="Тег",
        to="booking.BookingTag",
        on_delete=models.CASCADE,
        unique=False,
        related_name="group_status_through",
    )

    class Meta:
        managed = False
        db_table = "booking_tags_group_status_through"
        unique_together = ('group_status', 'tag')
        verbose_name = "Групповой статус-Тег"
        verbose_name_plural = "Групповые статусы-Теги"

    def __str__(self):
        return f"{self.group_status} {self.tag}"


class ClientGroupStatusTagThrough(models.Model):
    client_group_status = models.OneToOneField(
        verbose_name="Статус",
        to="booking.ClientAmocrmGroupStatus",
        on_delete=models.CASCADE,
        related_name="booking_tag_through",
        primary_key=True,
    )
    tag = models.ForeignKey(
        verbose_name="Тег",
        to="booking.BookingTag",
        on_delete=models.CASCADE,
        unique=False,
        related_name="client_group_status_through",
    )

    class Meta:
        managed = False
        db_table = "booking_tags_client_group_status_through"
        unique_together = ('client_group_status', 'tag')
        verbose_name = "Групповой статус-Тег дял клиента"
        verbose_name_plural = "Групповые статусы-Теги для клиентов"

    def __str__(self):
        return f"{self.client_group_status} {self.tag}"
