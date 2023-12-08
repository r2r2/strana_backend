from src.mortgage_calculator.entities import BaseMortgageCase
from src.mortgage_calculator.models import CreateMortgageTicketSchema


class CreateMortgageTicketCase(BaseMortgageCase):
    def __init__(self):
        ...

    async def __call__(self, payload: CreateMortgageTicketSchema) -> None:
        pass
