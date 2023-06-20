from common import cfields, mixins, orm
from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from common.models import TimeBasedMixin

from ..entities import BaseTextBlockRepo


class LkType(mixins.Choices):
    BROKER: str = "lk_broker", "ЛК Брокера"
    CLIENT: str = "lk_client", "ЛК Клиента"


class TextBlock(Model, TimeBasedMixin):
    """
    Текстовый блок.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    title: str = fields.TextField(description="Заголовок блока", null=True)
    text: str = fields.TextField(description="Текст блока", null=True)
    slug: str = fields.CharField(
        description="Слаг текстового блока",
        max_length=100,
        unique=True,
    )
    lk_type: str = cfields.CharChoiceField(
        description="Сервис ЛК, в котором применяется текстовый блок",
        max_length=10,
        choice_class=LkType,
    )
    description: str = fields.TextField(description="Описание назначения текстового блока", null=True)

    class Meta:
        table = "text_block_text_block"


class TextBlockRepo(BaseTextBlockRepo, CRUDMixin):
    """
    Репозиторий текстовых блоков.
    """
    model = TextBlock
    q_builder: orm.QBuilder = orm.QBuilder(TextBlock)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(TextBlock)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(TextBlock)
