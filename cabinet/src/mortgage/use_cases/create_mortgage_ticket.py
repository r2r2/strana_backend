import asyncio
from typing import Any

import structlog
from tortoise.transactions import in_transaction

from common.amocrm import AmoCRM
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import BookingRepo, Booking
from src.cities.repos import City, CityRepo
from src.mortgage.constants import ProofOfIncome
from src.mortgage.entities import BaseMortgageCase
from src.mortgage.exceptions import (
    MortgageFormNotFoundError,
    MortgageCalculatorConditionNotFoundError,
    MortgageProgramNotFoundError,
    MortgageBankNotFoundError,
    MortgageApplicationStatusNotFoundError,
)
from src.mortgage.models import CreateMortgageTicketSchema
from src.mortgage.models.create_ticket import SelectedOfferSchema
from src.mortgage.repos import (
    MortgageDeveloperTicketRepo,
    MortgageFormRepo,
    MortgageBankRepo,
    MortgageProgramRepo,
    MortgageApplicationStatusRepo,
    MortgageForm,
    MortgageConditionMatrixRepo,
    MortgageCalculatorConditionRepo,
    MortgageCalculatorCondition,
    MortgageProgram,
    MortgageBank,
    MortgageApplicationStatus,
    MortgageOffer,
    MortgageOfferRepo,
    MortgageDeveloperTicket,
)
from src.properties.constants import PropertyTypes


class CreateMortgageTicketCase(BaseMortgageCase):
    def __init__(
        self,
        mortgage_cond_matrix_repo: type[MortgageConditionMatrixRepo],
        mortgage_calc_cond_repo: type[MortgageCalculatorConditionRepo],
        mortgage_dev_ticket_repo: type[MortgageDeveloperTicketRepo],
        mortgage_form_repo: type[MortgageFormRepo],
        mortgage_bank_repo: type[MortgageBankRepo],
        mortgage_program_repo: type[MortgageProgramRepo],
        mortgage_application_status_repo: type[MortgageApplicationStatusRepo],
        mortgage_offer_repo: type[MortgageOfferRepo],
        booking_repo: type[BookingRepo],
        amocrm_class: type[AmoCRM],
    ):
        self.mortgage_cond_matrix_repo: MortgageConditionMatrixRepo = mortgage_cond_matrix_repo()
        self.mortgage_calc_cond_repo: MortgageCalculatorConditionRepo = mortgage_calc_cond_repo()
        self.mortgage_dev_ticket_repo: MortgageDeveloperTicketRepo = mortgage_dev_ticket_repo()
        self.mortgage_form_repo: MortgageFormRepo = mortgage_form_repo()
        self.mortgage_bank_repo: MortgageBankRepo = mortgage_bank_repo()
        self.mortgage_program_repo: MortgageProgramRepo = mortgage_program_repo()
        self.mortgage_application_status_repo: MortgageApplicationStatusRepo = mortgage_application_status_repo()
        self.mortgage_offer_repo: MortgageOfferRepo = mortgage_offer_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)
        self.payload: CreateMortgageTicketSchema | None = None

    async def __call__(self, payload: CreateMortgageTicketSchema) -> None:
        self.logger.info(f"Запрос на создание заявки на ипотеку. {payload=}")
        self.payload: CreateMortgageTicketSchema = payload
        booking: Booking = await self._get_booking()
        status: MortgageApplicationStatus = await self._get_status(booking=booking)
        async with in_transaction(connection_name='cabinet'):
            form_data: MortgageForm = await self._create_form_data()
            calculator_condition: MortgageCalculatorCondition = await self._create_calculator_condition()
            offers: list[MortgageOffer] = await self._create_offers()

            data: dict[str, Any] = dict(
                booking=booking,
                form_data=form_data,
                calculator_condition=calculator_condition,
                status=status,
                offers=offers,
            )
            await self._create_mortgage_ticket(data=data)
        asyncio.create_task(self._send_amo_note(lead_id=booking.amocrm_id))

    async def _create_mortgage_ticket(self, data: dict[str, Any]) -> None:
        self.logger.info(f"Создание заявки на ипотеку. {data=}")
        offers: list[MortgageOffer] = data.pop("offers")
        mortgage_dev_ticket: MortgageDeveloperTicket = await self.mortgage_dev_ticket_repo.create(data=data)
        await mortgage_dev_ticket.offers.add(*offers)

    async def _get_booking(self) -> Booking:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=self.payload.booking_id),
            related_fields=["amocrm_status"],
        )
        if not booking:
            raise BookingNotFoundError
        return booking

    async def _create_form_data(self) -> MortgageForm:
        form_data: MortgageForm = await self.mortgage_form_repo.create(
            data=self.payload.client.dict(exclude_none=True)
        )
        if not form_data:
            raise MortgageFormNotFoundError
        return form_data

    async def _create_calculator_condition(self) -> MortgageCalculatorCondition:
        data: dict[str, Any] = dict(
            cost_before=self.payload.values.property_cost,
            initial_fee_before=self.payload.values.initial_fee,
            until=self.payload.values.credit_term,
            proof_of_income=self.payload.values.income_confirmation,
        )
        calculator_condition: MortgageCalculatorCondition = await self.mortgage_calc_cond_repo.create(
            data=data,
        )
        if not calculator_condition:
            raise MortgageCalculatorConditionNotFoundError

        programs: list[MortgageProgram] = await self._get_mortgage_programs()
        banks: list[MortgageBank] = await self._get_mortgage_banks()

        await calculator_condition.programs.add(*programs)
        await calculator_condition.banks.add(*banks)

        return calculator_condition

    async def _get_mortgage_programs(self) -> list[MortgageProgram | None]:
        programs: list[MortgageProgram | None] = []
        if self.payload.values.mortgage_programs:
            programs: list[MortgageProgram] = await self.mortgage_program_repo.list(
                filters=dict(slug__in=self.payload.values.mortgage_programs),
            )
        return programs

    async def _get_mortgage_banks(self) -> list[MortgageBank | None]:
        banks: list[MortgageBank | None] = []
        if self.payload.values.banks:
            banks: list[MortgageBank] = await self.mortgage_bank_repo.list(
                filters=dict(uid__in=self.payload.values.banks),
            )
        return banks

    async def _get_status(self, booking: Booking) -> MortgageApplicationStatus:
        filters: dict[str, Any] = dict(
            amocrm_statuses__in=[booking.amocrm_status],
        )
        status: MortgageApplicationStatus = await self.mortgage_application_status_repo.retrieve(
            filters=filters,
        )
        if not status:
            raise MortgageApplicationStatusNotFoundError
        return status

    async def _create_offers(self) -> list[MortgageOffer]:
        offers: list[MortgageOffer] = []
        for offer in self.payload.offers:
            offers.append(await self._create_mortgage_offer(offer=offer))
        return offers

    async def _create_mortgage_offer(self, offer: SelectedOfferSchema) -> MortgageOffer:
        bank: MortgageBank = await self._get_bank(offer=offer)
        program: MortgageProgram = await self._get_program(offer=offer)
        data: dict[str, Any] = dict(
            monthly_payment=offer.monthly_payment,
            percent_rate=offer.percent_rate,
            credit_term=offer.credit_term,
            external_code=offer.external_code,
            name=offer.name,
            uid=offer.uid,
            bank=bank,
            program=program,
        )
        mortgage_offer: MortgageOffer = await self.mortgage_offer_repo.create(
            data=data,
        )
        return mortgage_offer

    async def _get_bank(self, offer: SelectedOfferSchema) -> MortgageBank:
        bank: MortgageBank = await self.mortgage_bank_repo.retrieve(
            filters=dict(uid=offer.uid),
        )
        if not bank:
            raise MortgageBankNotFoundError
        return bank

    async def _get_program(self, offer: SelectedOfferSchema) -> MortgageProgram:
        program: MortgageProgram = await self.mortgage_program_repo.retrieve(
            filters=dict(slug=offer.program),
        )
        if not program:
            raise MortgageProgramNotFoundError
        return program

    async def _send_amo_note(self, lead_id: int) -> None:
        """
        Отправка заметки в АМО
        """
        amo_note_builder: AmoLeadNoteBuilder = AmoLeadNoteBuilder(payload=self.payload)
        message: str = await amo_note_builder.build()
        async with await self.amocrm_class() as amocrm:
            await amocrm.send_lead_note(
                lead_id=lead_id,
                message=message,
            )


class AmoLeadNoteBuilder:
    """
    Строитель заметки в АМО
    """
    _DEFAULT_MESSAGE: str = 'Не указано'

    def __init__(self, payload: CreateMortgageTicketSchema):
        self.payload: CreateMortgageTicketSchema = payload
        self.message: str = ''

        self.city_repo: CityRepo = CityRepo()
        self.mortgage_program_repo: MortgageProgramRepo = MortgageProgramRepo()

    async def build(self) -> str:
        await self._build_desired_parameters()
        await self._build_selected_offers()
        await self._build_personal_data()
        return self.message

    async def _build_desired_parameters(self) -> None:
        city_name: str = await self._get_city_name()
        property_type: str = await self._get_property_type()
        self.message += f"""
            Заявка на ипотеку:
                Город: {city_name}
                Тип объекта: {property_type}
                Стоимость: {self.payload.values.property_cost} руб.
                Первоначальный взнос: {self.payload.values.initial_fee}%
                Срок: {self.payload.values.credit_term} лет
        """
        income_confirmation: str = self.payload.values.income_confirmation
        if income_confirmation and income_confirmation != ProofOfIncome.NO_NEEDED:
            income_confirmation: str = ProofOfIncome.to_label(income_confirmation)
            self.message += f"""Подтверждение дохода: {income_confirmation}""".lstrip("\n")

    async def _build_selected_offers(self) -> None:
        selected_offers: list[str] = []
        for offer in self.payload.offers:
            program_name: str = await self._get_program_name(offer=offer)
            of: str = f"""
                Ипотечная программа: {program_name}
                Выбранный банк: {offer.bank_name}
                Ежемесячный платеж: {offer.monthly_payment} руб.
                Процентная ставка: {offer.percent_rate}%
            """
            selected_offers.append(of)
        selected_offers: str = '\n'.join(selected_offers)
        self.message += f"""Список заявок:{selected_offers}"""

    async def _build_personal_data(self) -> None:
        patronymic: str = self.payload.client.patronymic or self._DEFAULT_MESSAGE
        self.message += f"""
            Контактные данные:
                Имя: {self.payload.client.name}
                Фамилия: {self.payload.client.surname}
                Отчество: {patronymic}
                Телефон: {self.payload.client.phone}
        """

    async def _get_city_name(self) -> str:
        city: City = await self.city_repo.retrieve(
            filters=dict(slug=self.payload.values.city),
        )
        if not city:
            return self._DEFAULT_MESSAGE
        return city.name

    async def _get_property_type(self) -> str:
        property_type: str = PropertyTypes.to_label(self.payload.values.property_type)
        if not property_type:
            return self._DEFAULT_MESSAGE
        return property_type

    async def _get_program_name(self, offer: SelectedOfferSchema) -> str:
        program: MortgageProgram = await self.mortgage_program_repo.retrieve(
            filters=dict(slug=offer.program),
        )
        if not program:
            return self._DEFAULT_MESSAGE
        return program.name
