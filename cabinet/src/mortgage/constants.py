from common import mixins


class ProofOfIncome(mixins.Choices):
    """
    Выборочное подтверждение прихода
    """
    NO_NEEDED: str = "no_needed", "Без справок"
    NDFL: str = "ndfl", "2-НДФЛ"


class MortgageApprove(mixins.Choices):
    """
    Выборочное подтверждение ипотеки в матрице
    """
    YES: str = "yes", "Да 1"
    NO: str = "no", "Нет"
