# pylint: disable=invalid-str-returned
from common import cfields, mixins
from common.orm.mixins import CRUDMixin
from tortoise import Model, fields

from ..entities import BaseTemplateRepo


class TemplateTypeType(mixins.Choices):
    IP: str = "IP", "ИП"
    OOO: str = "OOO", "ООО"


class DocTemplate(Model):
    """
    Репозиторий шаблонов договоров
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    project: fields.ForeignKeyNullableRelation["Project"] = fields.ForeignKeyField(
        model_name="models.Project",
        on_delete=fields.CASCADE,
        related_name="templates",
        description="ЖК"
    )
    agreement_type: fields.ForeignKeyNullableRelation["AgreementType"] = fields.ForeignKeyField(
        model_name="models.AgreementType",
        on_delete=fields.CASCADE,
        related_name="templates",
        description="Тип документа"
    )
    type: str = cfields.CharChoiceField(description="Тип шаблона", max_length=50,
                                        choice_class=TemplateTypeType, null=False)
    template_name: str = fields.CharField(description='Название шаблона', max_length=150)

    def __str__(self) -> str:
        return self.template_name

    class Meta:
        table = "docs_templates"


class DocTemplateRepo(BaseTemplateRepo, CRUDMixin):
    """
    Репозиторий воронки
    """
    model = DocTemplate
