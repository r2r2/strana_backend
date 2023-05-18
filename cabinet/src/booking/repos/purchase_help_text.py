from typing import Any, Optional, Union

from tortoise import fields, Model
from tortoise.query_utils import Prefetch, Q
from tortoise.queryset import QuerySet, QuerySetSingle

from common import cfields, orm
from common.orm.mixins import CreateMixin, RetrieveMixin

from ..constants import OnlinePurchaseSteps, PaymentMethods
from ..entities import BaseBookingRepo


class PurchaseHelpText(Model):
    """
    Текст тултипа "Как купить онлайн?"
    """

    id: int = fields.IntField(description="ID", pk=True)
    text: str = fields.TextField(description="Текст")
    booking_online_purchase_step: str = cfields.CharChoiceField(
        description="Стадия онлайн-покупки", max_length=50, choice_class=OnlinePurchaseSteps
    )
    payment_method: str = cfields.CharChoiceField(
        description="Способ покупки",
        max_length=20,
        choice_class=PaymentMethods,
    )
    maternal_capital: bool = fields.BooleanField(
        description="Тип покупки: Выбран 'Материнский капитал'"
    )
    certificate: bool = fields.BooleanField(description="Тип покупки: Выбран 'Жилищный сертификат'")
    loan: bool = fields.BooleanField(description="Тип покупки: Выбран 'Государственный займ'")

    default: bool = fields.BooleanField(description="Текст по-умолчанию", default=False)

    class Meta:
        table = "booking_purchase_help_text"


class PurchaseHelpTextRepo(BaseBookingRepo, CreateMixin, RetrieveMixin):
    """
    Репозиторий тултипов "Как купить онлайн?"
    """

    model = PurchaseHelpText
    q_builder: orm.QBuilder = orm.QBuilder(PurchaseHelpText)
