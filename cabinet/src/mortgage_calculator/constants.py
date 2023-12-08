from common import mixins


class ProofOfIncome(mixins.Choices):
    """
    Выборочное подтверждение прихода
    """
    CASE: str = "Case", "КЕЙС"
    TEST: str = "Test", "ТЕСТ"


class MortgageApprove(mixins.Choices):
    """
    Выборочное подтверждение ипотеки в матрице
    """
    YES: str = "Yes", "Да 1"
    NO: str = "No", "Нет"
