from datetime import datetime

from tortoise import Model, fields


class AgencyAdditionalAgreementCreatingData(Model):
    """
    Данные для формирования ДС через админку.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    projects: fields.ManyToManyRelation["EventTag"] = fields.ManyToManyField(
        description="Проекты",
        model_name="models.Project",
        related_name="additional_data",
        on_delete=fields.SET_NULL,
        through="additional_data_projects",
        backward_key="additional_data_id",
        forward_key="project_id",
    )
    agencies: fields.ManyToManyRelation["EventTag"] = fields.ManyToManyField(
        description="Агентства",
        model_name="models.Agency",
        related_name="additional_data",
        on_delete=fields.SET_NULL,
        through="additional_data_agencies",
        backward_key="additional_data_id",
        forward_key="agency_id",
    )
    reason_comment: str = fields.CharField(description="Комментарий (администратора)", max_length=300)
    additionals_created = fields.BooleanField(
        description="ДС сгенерированы",
        default=False,
    )
    created_at: datetime = fields.DatetimeField(description="Когда создано", auto_now_add=True)

    class Meta:
        table = "agencies_additional_agreement_creating_data"
