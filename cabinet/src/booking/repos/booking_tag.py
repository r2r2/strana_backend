from common import cfields
from common.orm.mixins import CreateMixin, ListMixin
from tortoise import Model, fields

from ..constants import BookingTagStyle
from ..entities import BaseBookingRepo


class BookingTag(Model):
    """
    Тег сделки
    """

    id: int = fields.IntField(description="ID", pk=True)
    label: str = fields.CharField(max_length=100, description='Название')
    style: str = cfields.CharChoiceField(
        description='Стиль',
        max_length=20,
        choice_class=BookingTagStyle,
        default=BookingTagStyle.DEFAULT,
    )
    slug: str = fields.CharField(max_length=255, description='Слаг тега')
    priority: int = fields.IntField(
        description='Приоритет. Чем меньше приоритет - тем выше выводится тег в списке',
        null=True,
        blank=True,
    )
    is_active = fields.BooleanField(
        verbose_name="Активность", default=False, description="Неактивные теги не выводятся на сайте"
    )
    group_statuses: fields.ManyToManyRelation["AmocrmGroupStatus"] = fields.ManyToManyField(
        description="Теги сделок",
        model_name="models.AmocrmGroupStatus",
        related_name="booking_tags",
        on_delete=fields.SET_NULL,
        through="booking_tags_group_status_through",
        backward_key="tag_id",
        forward_key="group_status_id",
    )

    client_group_statuses: fields.ManyToManyRelation["ClientAmocrmGroupStatus"] = fields.ManyToManyField(
        description="Теги сделок для клиентов",
        model_name="models.ClientAmocrmGroupStatus",
        related_name="booking_tags",
        on_delete=fields.SET_NULL,
        through="booking_tags_client_group_status_through",
        backward_key="tag_id",
        forward_key="client_group_status_id",
    )

    def __str__(self):
        return self.label

    class Meta:
        table = "booking_bookingtag"


class BookingTagRepo(BaseBookingRepo, CreateMixin, ListMixin):
    """
    Репозиторий тега бронирования
    """

    model = BookingTag


class BookingTagsGroupStatusThrough(Model):
    id: int = fields.IntField(description="ID", pk=True)
    group_status: fields.ForeignKeyRelation["AmocrmGroupStatus"] = fields.ForeignKeyField(
        model_name="models.AmocrmGroupStatus",
        related_name="booking_tag_through",
        description="Статус",
        on_delete=fields.CASCADE,
    )
    tag: fields.ForeignKeyRelation[BookingTag] = fields.ForeignKeyField(
        model_name="models.BookingTag",
        related_name="group_status_through",
        description="Тег",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "booking_tags_group_status_through"


class BookingTagsClientGroupStatusThrough(Model):
    id: int = fields.IntField(description="ID", pk=True)
    client_group_status: fields.ForeignKeyRelation["ClientAmocrmGroupStatus"] = fields.ForeignKeyField(
        model_name="models.ClientAmocrmGroupStatus",
        related_name="booking_tag_through",
        description="Статус",
        on_delete=fields.CASCADE,
    )
    tag: fields.ForeignKeyRelation[BookingTag] = fields.ForeignKeyField(
        model_name="models.BookingTag",
        related_name="client_group_status_through",
        description="Тег",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "booking_tags_client_group_status_through"
