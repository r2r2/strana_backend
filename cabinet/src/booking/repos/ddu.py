from datetime import date, datetime
from typing import Optional, Any, Union

from tortoise import fields, Model
from tortoise.fields import ForeignKeyRelation, ReverseRelation
from common import cfields, orm
from common.orm.mixins import CRUDMixin, SCountMixin

from ..constants import MaritalStatus, RelationStatus
from ..entities import BaseBookingRepo


class DDU(Model):
    """
    ДДУ
    """

    id: int = fields.IntField(description="ID", pk=True)
    create_datetime: datetime = fields.DatetimeField(
        description="Дата и время создания ДДУ", null=True
    )
    participants: ReverseRelation["DDUParticipant"]

    account_number: str = fields.CharField(description="Номер счёта", max_length=50)
    payees_bank: str = fields.CharField(description="Банк получателя", max_length=50)
    bik: str = fields.CharField(description="БИК", max_length=50)
    corresponding_account: str = fields.CharField(description="Кор. счёт", max_length=50)
    bank_inn: str = fields.CharField(description="ИНН банка", max_length=50)
    bank_kpp: str = fields.CharField(description="КПП банка", max_length=50)

    change_diffs: list = cfields.JSONField(description="Изменения ДДУ", default=[])
    files: Union[list, dict] = cfields.MutableDocumentContainerField(description="Файлы", null=True)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        table = "booking_ddu"


class DDUParticipant(Model):
    """
    Участник договора
    """

    ddu: ForeignKeyRelation[DDU] = fields.ForeignKeyField("models.DDU", related_name="participants")
    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(description="Имя", max_length=50)
    surname: str = fields.CharField(description="Фамилия", max_length=50)
    patronymic: str = fields.CharField(description="Отчество", max_length=50)
    inn: str = fields.CharField(description='ИНН', max_length=50, null=True)
    is_main_contact: bool = fields.BooleanField(
        description="Это и есть контакт в AmoCRM", default=False
    )

    passport_serial: Optional[str] = fields.CharField(
        description="Серия паспорта", max_length=4, null=True
    )
    passport_number: Optional[str] = fields.CharField(
        description="Номер паспорта", max_length=6, null=True
    )
    passport_issued_by: Optional[str] = fields.CharField(
        description="Паспорт, кем выдан", max_length=150, null=True
    )
    passport_department_code: Optional[str] = fields.CharField(
        description="Паспорт, код подразделения", max_length=7, null=True
    )
    passport_issued_date: Optional[date] = fields.DateField(
        description="Дата выдачи паспорта", null=True
    )

    marital_status: str = cfields.CharChoiceField(
        description="Семейное положение", max_length=24, choice_class=MaritalStatus, null=True
    )
    relation_status: str = cfields.CharChoiceField(
        description="Кем приходится", max_length=24, choice_class=RelationStatus, null=True
    )
    is_not_resident_of_russia: bool = fields.BooleanField(description="Не резидент России")
    has_children: bool = fields.BooleanField(description="Есть дети")
    is_older_than_fourteen: Optional[bool] = fields.BooleanField(
        description="Старше 14 лет", null=True
    )

    files: Union[list, dict] = cfields.MutableDocumentContainerField(description="Файлы", null=True)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        table = "booking_ddu_participant"
        ordering = ["id"]


class DDURepo(BaseBookingRepo, CRUDMixin, SCountMixin):
    """
    Репозиторий ДДУ
    """

    model = DDU
    q_builder: orm.QBuilder = orm.QBuilder(DDU)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(DDU)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(DDU)


class DDUParticipantRepo(BaseBookingRepo, CRUDMixin, SCountMixin):
    """
    Репозиторий ДДУ
    """

    model = DDUParticipant
    q_builder: orm.QBuilder = orm.QBuilder(DDUParticipant)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(DDUParticipant)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(DDUParticipant)
