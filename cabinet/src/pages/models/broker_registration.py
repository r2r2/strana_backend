from typing import Optional, Any

from ..entities import BasePageModel


class RequestBrokerRegistrationModel(BasePageModel):
    """
    Модель запроса регистрации брокера
    """

    class Config:
        orm_mode = True


class ResponseBrokerRegistrationModel(BasePageModel):
    """
    Модель ответа регистрации брокера
    """

    new_pwd_image: Optional[dict[str, Any]]
    login_pwd_image: Optional[dict[str, Any]]
    forgot_pwd_image: Optional[dict[str, Any]]
    forgot_send_image: Optional[dict[str, Any]]
    login_email_image: Optional[dict[str, Any]]
    enter_agency_image: Optional[dict[str, Any]]
    confirm_send_image: Optional[dict[str, Any]]
    enter_personal_image: Optional[dict[str, Any]]
    enter_password_image: Optional[dict[str, Any]]
    accept_contract_image: Optional[dict[str, Any]]
    confirmed_email_image: Optional[dict[str, Any]]

    class Config:
        orm_mode = True
