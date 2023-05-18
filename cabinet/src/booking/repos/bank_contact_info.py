from tortoise import Model, fields

from common import orm
from common.orm.mixins import SCountMixin, CRUDMixin

from ..entities import BaseBookingRepo


class BankContactInfo(Model):
    """
    Данные для связи с банком
    """

    id: int = fields.IntField(description="ID", pk=True)
    bank_name: str = fields.CharField(description="Название банка", max_length=100)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        table = "booking_bank_contact_info"


class BankContactInfoRepo(BaseBookingRepo, CRUDMixin, SCountMixin):
    """
    Репозиторий данных для связи с банком
    """

    model = BankContactInfo
    q_builder: orm.QBuilder = orm.QBuilder(BankContactInfo)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(BankContactInfo)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(BankContactInfo)
