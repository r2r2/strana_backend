# pylint: disable=invalid-str-returned
from common import cfields, mixins, orm
from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from ..entities import BaseTemplateRepo


class AdditionalTemplateType(mixins.Choices):
    IP: str = "IP", "ИП"
    OOO: str = "OOO", "ООО"


class AdditionalAgreementTemplate(Model):
    """
    Шаблоны дополнительных соглашений
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    project: fields.ForeignKeyNullableRelation["Project"] = fields.ForeignKeyField(
        model_name="models.Project",
        on_delete=fields.CASCADE,
        related_name="additional_templates",
        description="ЖК"
    )
    type: str = cfields.CharChoiceField(description="Тип шаблона", max_length=50,
                                        choice_class=AdditionalTemplateType, null=True)
    template_name: str = fields.CharField(description='Название шаблона', max_length=150)

    def __str__(self) -> str:
        return self.template_name

    class Meta:
        table = "additional_agreement_templates"


class AdditionalAgreementTemplateRepo(BaseTemplateRepo, CRUDMixin):
    """
    Репозиторий шаблонов дополнительных соглашений
    """
    model = AdditionalAgreementTemplate
    q_builder: orm.QBuilder = orm.QBuilder(AdditionalAgreementTemplate)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(AdditionalAgreementTemplate)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(AdditionalAgreementTemplate)
