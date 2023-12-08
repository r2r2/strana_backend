from src.booking.repos import Booking
from src.mortgage_calculator.repos import MortgageConditionMatrixRepo, MortgageConditionMatrix


class MortgageTicketCheckerService:
    def __init__(self, booking: Booking):
        self.booking: Booking = booking
        self.condition_matrix_repo: MortgageConditionMatrixRepo = MortgageConditionMatrixRepo()

    async def check(self) -> tuple[bool, bool]:
        """
        Проверка возможности подать заявку на ипотеку.
        Returns:
            is_booking_in_matrix: Находится ли статус сделки в статусах матрицы
            is_eligible_for_mortgage: Подходит ли сделка для подачи заявки на ипотеку
        """
        await self.booking.fetch_related("amocrm_status")
        matrix_conditions: list[MortgageConditionMatrix] = await self.condition_matrix_repo.list(
            prefetch_fields=["amocrm_statuses"],
        )
        is_booking_in_matrix: bool = True
        is_eligible_for_mortgage: bool | None = self._check_conditions(matrix_conditions)

        if is_eligible_for_mortgage is None:
            is_booking_in_matrix: bool = False
            is_eligible_for_mortgage: bool = False

        return is_booking_in_matrix, is_eligible_for_mortgage

    def _check_conditions(self, matrix_conditions: list[MortgageConditionMatrix]) -> bool | None:
        """
        Проверка условий.
        """
        for condition in matrix_conditions:
            if self.booking.amocrm_status in condition.amocrm_statuses:
                return (self.booking.agent is not None) == condition.is_there_agent
