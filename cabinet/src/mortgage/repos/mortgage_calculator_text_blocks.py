from datetime import datetime

from tortoise import models, fields

from common.orm.entities import BaseRepo
from common.orm.mixins import CRUDMixin


class MortgageTextBlock(models.Model):
    """
    Текстовые блоки для ик.
    """

    title: str = fields.TextField(
        description="Заголовок блока",
        null=True,
        help_text="H1 заголовок страницы / слайд-панели",
    )
    text: str = fields.TextField(
        description="Текст блока",
        null=True,
    )
    slug: str = fields.CharField(
        max_length=100,
        description="Слаг текстового блока",
    )
    lk_type: str = fields.CharField(
        description="Сервис ЛК, в котором применяется текстовый блок",
        max_length=10,
        null=True,
    )
    description: str = fields.TextField(
        description="Описание назначения текстового блока",
        null=True,
    )
    created_at: datetime = fields.DatetimeField(
        description="Дата и время создания",
        auto_now_add=True,
    )
    updated_at: datetime = fields.DatetimeField(
        description="Дата и время обновления",
        auto_now=True,
    )
    cities: fields.ManyToManyRelation["City"] = fields.ManyToManyField(
        model_name="models.City",
        related_name="mortgage_text_blocks",
        through="mortgage_calculator_text_block_city_through",
        description="Города",
        null=True,
        on_delete=fields.CASCADE,
        backward_key="mortgage_text_block_id",
        forward_key="city_id",
    )

    def __str__(self) -> str:
        return self.slug

    class Meta:
        table = "mortgage_calculator_text_blocks"


class MortgageCalculatorTextBlockCityThrough(models.Model):
    """
    Отношения ип калькулят текстовых блоков к городам.
    """
    id: int = fields.IntField(description="ID", pk=True)
    mortgage_text_block: fields.ForeignKeyRelation[MortgageTextBlock] = fields.ForeignKeyField(
        model_name="models.MortgageTextBlock",
        related_name="mortgage_text_block_city_through",
        description="Текстовые блоки",
        on_delete=fields.CASCADE,
    )
    city: fields.ForeignKeyRelation["City"] = fields.ForeignKeyField(
        model_name="models.City",
        related_name="mortgage_text_block_city_through",
        description="Города",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "mortgage_calculator_text_block_city_through"


class MortgageTextBlockRepo(BaseRepo, CRUDMixin):
    """
    Репозиторий текстового блока
    """
    model = MortgageTextBlock
