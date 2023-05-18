from typing import Optional

from tortoise import Model, fields


class AdditionalAgreementStatus(Model):
    id: int = fields.IntField(description="ID", pk=True, index=True)
    name: str = fields.CharField(description="Название статуса", max_length=100)
    description: Optional[str] = fields.TextField(description="Описание статуса", null=True)

    class Meta:
        table = "additional_agreement_status"
