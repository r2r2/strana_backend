from common import cfields
from typing import Optional, Any
from tortoise import Model, fields

from common.orm.mixins import CreateMixin, RetrieveMixin
from ..entities import BasePageRepo


class BrokerRegistration(Model):
    """
    Регистрация брокера
    """

    id: int = fields.IntField(description="ID", pk=True)
    new_pwd_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение новый пароль", max_length=500, null=True
    )
    login_pwd_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение логин пароль", max_length=500, null=True
    )
    forgot_pwd_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение забыл пароль", max_length=500, null=True
    )
    forgot_send_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение забыл пароль письмо", max_length=500, null=True
    )
    login_email_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение логин почта", max_length=500, null=True
    )
    enter_agency_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение ввод агенства", max_length=500, null=True
    )
    confirm_send_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение подтвеждение отправлено", max_length=500, null=True
    )
    enter_personal_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение ввод данных", max_length=500, null=True
    )
    enter_password_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение ввод пароля", max_length=500, null=True
    )
    accept_contract_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение принятие договора", max_length=500, null=True
    )
    confirmed_email_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение почта подтверждена", max_length=500, null=True
    )

    def __str__(self) -> str:
        return self.__doc__.strip()

    class Meta:
        table = "pages_broker_registration"


class BrokerRegistrationRepo(BasePageRepo, CreateMixin, RetrieveMixin):
    """
    Репозиторий регистрации брокера
    """
    model = BrokerRegistration
