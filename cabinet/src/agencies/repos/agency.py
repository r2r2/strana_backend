# pylint: disable=arguments-renamed,invalid-str-returned

import re
from datetime import date, datetime
from typing import Any, List, Optional, Union
from tortoise.fields import ForeignKeyRelation

from common import cfields, orm
from common.files import FileCategory, FileContainer
from common.orm.mixins import CountMixin, DeleteMixin, ReadWriteMixin
from tortoise import Model, fields
from tortoise.exceptions import IntegrityError, ValidationError
from tortoise.validators import Validator

from ..constants import AgencyType
from ..entities import BaseAgencyRepo


class SRNValidator(Validator):
    """
    A validator to validate state registration number
    """

    def __init__(self):
        self.srn_re = re.compile('^([15][0-9]{12})?$')
        self.srnip_re = re.compile('^(3[0-9]{14})?$')

    def __call__(self, value: Any):
        if not any([self.srn_re.match(value), self.srnip_re.match(value)]):
            raise ValidationError(f"Value '{value}' does not match regex "
                                  f"'{self.srnip_re.pattern}', '{self.srn_re.pattern}'")


class Agency(Model):
    """
    Агентство
    """

    types = AgencyType()

    id: int = fields.IntField(description="ID", pk=True)
    inn: str = fields.CharField(description="ИНН", max_length=30)
    city: str = fields.CharField(description="Город", max_length=30)
    name: Optional[str] = fields.CharField(description="Имя", max_length=100, null=True)

    type: Optional[str] = cfields.CharChoiceField(
        description="Тип", max_length=20, choice_class=AgencyType, null=True
    )
    general_type: ForeignKeyRelation["AgencyGeneralType"] = fields.ForeignKeyField(
        description="Тип агентства (агрегатор/АН)",
        model_name="models.AgencyGeneralType",
        on_delete=fields.SET_NULL,
        related_name="agencies",
        null=True,
    )
    files: Union[list, dict] = cfields.MutableDocumentContainerField(description="Файлы", null=True)

    is_deleted: bool = fields.BooleanField(description="Удалено", default=False)
    is_approved: bool = fields.BooleanField(description="Подтверждено", default=False)
    is_imported: bool = fields.BooleanField(description="Импортировано", default=False)

    tags: Union[list, dict] = fields.JSONField(description="Тэги", null=True)
    amocrm_id: Optional[int] = fields.BigIntField(description="ID AmoCRM", null=True)

    created_at: datetime = fields.DatetimeField(
        description="Дата и время регистрации в базе", auto_now_add=True
    )

    state_registration_number: str = fields.CharField(description="ОГРН/ОРНИП", max_length=15, null=True,
                                                      validators=[SRNValidator()])
    legal_address: str = fields.TextField(description="Юридически адрес", null=True)
    bank_name: str = fields.CharField(description="Название банка", max_length=100, null=True)
    bank_identification_code: str = fields.CharField(description="БИК", max_length=9, null=True)
    checking_account: str = fields.CharField(description="Расчетный счет", max_length=20, null=True)
    correspondent_account: str = fields.CharField(description="Корреспондентский счет", max_length=20, null=True)

    signatory_name: str = fields.CharField(description="Имя подписанта", max_length=50, null=True)
    signatory_surname: str = fields.CharField(description="Фамилия подписанта", max_length=50, null=True)
    signatory_patronymic: str = fields.CharField(description="Отчество подписанта", max_length=50, null=True)
    signatory_registry_number: str = fields.CharField(description="Номер регистрации в реестре",
                                                      max_length=100, null=True)
    signatory_sign_date: date = fields.DateField(description="Дата подписания", null=True)

    maintainer: fields.ReverseRelation['User']
    agreements: fields.ReverseRelation["AgencyAgreement"]
    acts: fields.ReverseRelation["AgencyAct"]
    agency_confirm_client_assign: fields.ReverseRelation["ConfirmClientAssign"]

    def __str__(self) -> str:
        return self.inn

    class Meta:
        table = "agencies_agency"
        ordering = ["-created_at"]


class AgencyRepo(BaseAgencyRepo, ReadWriteMixin, DeleteMixin, CountMixin):
    """
    Репозиторий агентства
    """
    model = Agency
    q_builder: orm.QBuilder = orm.QBuilder(Agency)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(Agency)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(Agency)

    async def update(self, model: Agency, data: dict[str, Any]) -> Agency:
        """
        Обновление агентства
        """
        for field, value in data.items():
            setattr(model, field, value)
        try:
            await model.save()
        except IntegrityError:
            model = None
        return model

    async def update_files(self, model: Agency, data: FileContainer) -> Agency:
        """Обновляет поле files"""
        update_slug_file_map = {}
        for existing_category in model.files:
            update_slug_file_map[existing_category.slug] = existing_category

        for new_category in data:
            update_slug_file_map[new_category.slug] = new_category

        result_files_field_data: List[FileCategory] = list(update_slug_file_map.values())
        data = dict(files=FileContainer(result_files_field_data))

        return await self.update(model=model, data=data)
