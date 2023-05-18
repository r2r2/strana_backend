from asyncio import Task
from typing import Any, Optional, Type

from common.amocrm import AmoCRM
from common.amocrm.leads.payment_method import (AmoCRMPaymentMethod,
                                                AmoCRMPaymentMethodMapping)
from src.booking.loggers.wrappers import booking_changes_logger

from ..constants import OnlinePurchaseSteps, PaymentMethods
from ..entities import BaseBookingCase
from ..exceptions import (BookingBadRequestError, BookingNotFoundError,
                          BookingPaymentMethodNotFoundError,
                          BookingWrongStepError)
from ..mixins import BookingLogMixin
from ..models import BankContactInfoModel, RequestPaymentMethodSelectModel
from ..repos import BankContactInfo, BankContactInfoRepo, Booking, BookingRepo
from ..services import HistoryService, NotificationService
from ..types import BookingEmail, BookingSms


class PaymentMethodSelectCase(BaseBookingCase, BookingLogMixin):
    """
    Выбор способа покупки.

    Здесь же создаётся заявка на ипотеку или данные для связи с банком клиента.
    Если они создаются, то примечание отправляется в AmoCRM.

    Важно отметить, что в AmoCRM ограниченный специфичный набор вариантов выбора поля 'тип оплаты' -
    того, что имеется в виду под способом покупки у нас. Поэтому нельзя указать любую комбинацию.

    Также должны отправляться email и смс, если были отправлены данные для контакта с банком или
    заявка на ипотеку.
    """

    email_template_mortgage_request: str = "src/booking/templates/mortgage_request_created.html"
    email_template_bank_contact_info: str = "src/booking/templates/bank_contact_info_sent.html"
    _notification_template = "src/booking/templates/notifications/payment_method_select.json"
    _history_template = "src/booking/templates/history/payment_method_select.txt"

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        bank_contact_info_repo: Type[BankContactInfoRepo],
        amocrm_class: Type[AmoCRM],
        sms_class: Type[BookingSms],
        email_class: Type[BookingEmail],
        history_service: HistoryService,
        notification_service: NotificationService,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.bank_contact_info_repo: BankContactInfoRepo = bank_contact_info_repo()
        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.sms_class: Type[BookingSms] = sms_class
        self.email_class: Type[BookingEmail] = email_class

        self._history_service = history_service
        self._notification_service = notification_service
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Выбор способа покупки.",
        )

    async def __call__(
        self,
        booking_id: int,
        user_id: int,
        payload: RequestPaymentMethodSelectModel,
    ) -> Booking:
        filters: dict[str, Any] = dict(active=True, id=booking_id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["project", "property", "floor", "building", "ddu", "user"],
            prefetch_fields=["ddu__participants"],
        )

        if not booking:
            raise BookingNotFoundError

        previous_online_purchase_step = booking.online_purchase_step()
        self._check_step_requirements(booking)
        self._validate_data(payload)

        data = dict(
            payment_method=payload.payment_method,
            payment_method_selected=True,
            maternal_capital=payload.maternal_capital,
            housing_certificate=payload.housing_certificate,
            government_loan=payload.government_loan,
            client_has_an_approved_mortgage=payload.client_has_an_approved_mortgage,
            mortgage_request_selected=not payload.client_has_an_approved_mortgage,
        )
        booking: Booking = await self.booking_update(booking=booking, data=data)
        bank_contact_info: Optional[BankContactInfo] = None

        mortgage_request_created = False
        bank_contact_info_sent = False
        # Если у клиента есть одобренная ипотека - заполняем данные для связи с банком
        # Если нет - "создаём" заявку на ипотеку
        if payload.payment_method == PaymentMethods.MORTGAGE:
            if payload.client_has_an_approved_mortgage:
                bank_contact_info = await self._create_bank_contact_info(payload.bank_contact_info)
                booking = await self.booking_update(
                    booking=booking, data=dict(bank_contact_info=bank_contact_info)
                )
                bank_contact_info_sent = True
            else:
                mortgage_request_created = True

        # Оповещение, если клиент отправил данные для связи с банком или создал заявку на ипотеку
        if payload.payment_method == PaymentMethods.MORTGAGE:
            await self._notify_client(
                booking,
                mortgage_request_created=mortgage_request_created,
                bank_contact_info_sent=bank_contact_info_sent,
                previous_online_purchase_step=previous_online_purchase_step,
            )

        await self._amocrm_hook(
            booking=booking,
            bank_contact_info=bank_contact_info,
            mortgage_request_created=mortgage_request_created,
        )

        instruments = (
            payload.maternal_capital,
            payload.housing_certificate,
            payload.government_loan,
        )
        instruments_count = len([1 for instrument in instruments if instrument])
        history_params = {
            "payment_method": payload.payment_method,
            "maternal_capital": payload.maternal_capital,
            "housing_certificate": payload.housing_certificate,
            "government_loan": payload.government_loan,
            "instruments_count": instruments_count,
        }
        if (
            payload.payment_method == PaymentMethods.MORTGAGE
            and payload.client_has_an_approved_mortgage
        ):
            history_params["bank_name"] = payload.bank_contact_info.bank_name

        await self._history_service.execute(
            booking=booking,
            previous_online_purchase_step=previous_online_purchase_step,
            template=self._history_template,
            params=history_params,
        )

        return booking

    async def _create_bank_contact_info(
        self, bank_contact_info_payload: BankContactInfoModel
    ) -> BankContactInfo:
        """Создание данных для связи с банком."""
        bank_data = bank_contact_info_payload.dict()
        return await self.bank_contact_info_repo.create(data=bank_data)

    async def _notify_client(
        self,
        booking: Booking,
        *,
        mortgage_request_created: bool,
        bank_contact_info_sent: bool,
        previous_online_purchase_step: str
    ) -> None:
        """Уведомление клиента.

        Ему приходит смс и email, если он отправил данные
        для связи с банком или создал заявку на ипотеку.
        """
        # sms_task: Optional[Task] = self._send_sms(
        #     booking,
        #     mortgage_request_created=mortgage_request_created,
        #     bank_contact_info_sent=bank_contact_info_sent,
        # )
        # if sms_task is not None:
        #     await sms_task

        email_task: Optional[Task] = self._send_email(
            booking,
            mortgage_request_created=mortgage_request_created,
            bank_contact_info_sent=bank_contact_info_sent,
        )
        if email_task is not None:
            await email_task

        await self._notification_service(
            booking=booking,
            previous_online_purchase_step=previous_online_purchase_step,
            template=self._notification_template,
            params={"mortgage_request_created": mortgage_request_created},
        )

    @staticmethod
    def _get_bank_contact_info_sms_message() -> str:
        """Текст смс при отправке клиентом данных для связи с банком."""
        return (
            "Покупка квартиры.\n\n"
            "Данные банка, где одобрена ипотека находятся на проверке.\n\n"
            "Подробности в личном кабинете:\n"
            "www.strana.com/login"
        )

    @staticmethod
    def _get_mortgage_request_sms_message() -> str:
        """Текст смс при создании заявки на ипотеку."""
        return (
            "Покупка квартиры.\n\n"
            "Заявка на ипотеку отправлена. Ожидайте ответа от банка.\n\n"
            "Подробности в личном кабинете:\n"
            "www.strana.com/login"
        )

    def _send_sms(
        self, booking: Booking, *, mortgage_request_created: bool, bank_contact_info_sent: bool
    ) -> Optional[Task]:
        """Отправка смс."""
        message: str
        if mortgage_request_created:
            message = self._get_mortgage_request_sms_message()
        elif bank_contact_info_sent:
            message = self._get_bank_contact_info_sms_message()
        else:
            return None

        sms_options: dict[str, Any] = dict(phone=booking.user.phone, message=message)
        sms_service: Any = self.sms_class(**sms_options)
        return sms_service.as_task()

    def _send_email(
        self, booking: Booking, *, mortgage_request_created: bool, bank_contact_info_sent: bool
    ) -> Optional[Task]:
        """Отправка email."""
        template: str
        if mortgage_request_created:
            template = self.email_template_mortgage_request
        elif bank_contact_info_sent:
            template = self.email_template_bank_contact_info
        else:
            return None

        email_options: dict[str, Any] = dict(
            topic="Покупка квартиры",
            template=template,
            context=dict(booking=booking),
            recipients=[booking.user.email],
        )
        email_service: Any = self.email_class(**email_options)
        return email_service.as_task()

    # @logged_action(content="ВЫБОР СПОСОБА ПОКУПКИ | AMOCRM")
    async def _amocrm_hook(
        self,
        booking: Booking,
        bank_contact_info: Optional[BankContactInfo] = None,
        mortgage_request_created: bool = False,
    ) -> None:
        """amocrm hook"""
        # При переходе пользователя к этапу "оформление ДДУ" в сделке меняем тип оплаты
        # в свойство "Ипотека одобрена?" передаем значение "Да/Нет", если способ покупки "Ипотека"
        amocrm: AmoCRM
        async with await self.amocrm_class() as amocrm:
            data_for_update = {}
            if booking.payment_method == PaymentMethods.MORTGAGE:
                data_for_update["is_mortgage_approved"] = booking.client_has_an_approved_mortgage
            data_for_update["payment_method"] = AmoCRMPaymentMethod(
                mortgage=booking.payment_method == PaymentMethods.MORTGAGE,
                cash=booking.payment_method == PaymentMethods.CASH,
                installment_plan=booking.payment_method == PaymentMethods.INSTALLMENT_PLAN,
                certificate=booking.housing_certificate,
                loan=booking.government_loan,
                maternal_capital=booking.maternal_capital,
            )

            await amocrm.update_lead(lead_id=booking.amocrm_id, **data_for_update)

            # Отправляем примечания, если клиент заполнил данные для связи с банком или
            # данные для подачи заявки на ипотеку
            if bank_contact_info is not None:
                note_text = self._get_bank_contact_info_note_text(bank_contact_info)
                await amocrm.create_note(
                    lead_id=booking.amocrm_id, text=note_text, element="lead", note="common"
                )

            if mortgage_request_created:
                note_text = "Клиент намерен подать заявку на ипотеку через Страну"
                await amocrm.create_note(
                    lead_id=booking.amocrm_id, text=note_text, element="lead", note="common"
                )

    @classmethod
    def _get_bank_contact_info_note_text(cls, bank_contact_info: BankContactInfo) -> str:
        """Текст примечания в AmoCRM о данных для контакта с банком.

        Используется для клиентов, у которых есть одобренная ипотека.
        """
        return "Клиент внёс данные для связи с банком:\nНазвание банка: {}".format(
            bank_contact_info.bank_name
        )

    @classmethod
    def _get_amocrm_payment_method(
        cls, payload: RequestPaymentMethodSelectModel
    ) -> Optional[AmoCRMPaymentMethod]:
        """get_amocrm_payment_method"""
        payment_method = AmoCRMPaymentMethod(
            cash=payload.payment_method == PaymentMethods.CASH,
        )
        return AmoCRMPaymentMethodMapping.get(payment_method, None)

    @classmethod
    def _check_step_requirements(cls, booking: Booking) -> None:
        """Проверка текущего шага."""
        if booking.online_purchase_step() != OnlinePurchaseSteps.PAYMENT_METHOD_SELECT:
            raise BookingWrongStepError

    @classmethod
    def _validate_data(cls, payload: RequestPaymentMethodSelectModel) -> None:
        """Валидация входных данных."""
        if payload.payment_method == PaymentMethods.MORTGAGE:
            if payload.client_has_an_approved_mortgage:
                if payload.bank_contact_info is None:
                    raise BookingBadRequestError('Необходимо заполнить "Данные для связи с банком"')

        payment_method = AmoCRMPaymentMethod(
            cash=payload.payment_method == PaymentMethods.CASH,
            mortgage=payload.payment_method == PaymentMethods.MORTGAGE,
            installment_plan=payload.payment_method == PaymentMethods.INSTALLMENT_PLAN,
            maternal_capital=payload.maternal_capital,
            loan=payload.government_loan,
            certificate=payload.housing_certificate,
        )
        if payment_method not in AmoCRMPaymentMethodMapping:
            raise BookingPaymentMethodNotFoundError
