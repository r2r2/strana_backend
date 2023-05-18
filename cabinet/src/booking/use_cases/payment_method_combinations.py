from typing import Optional

from common.amocrm.leads.payment_method import AmoCRMPaymentMethodMapping

from ..constants import PaymentMethods
from ..models import PaymentMethodCombination


class PaymentMethodCombinationsCase:
    """Все возможные варианты способа покупки в AmoCRM."""

    def __call__(self) -> list[PaymentMethodCombination]:
        combinations: list[PaymentMethodCombination] = []
        for amocrm_payment_method in AmoCRMPaymentMethodMapping.keys():
            payment_method: Optional[str] = None
            if amocrm_payment_method.cash:
                payment_method = PaymentMethods.CASH  # наличные
            elif amocrm_payment_method.mortgage:
                payment_method = PaymentMethods.MORTGAGE  # ипотека
            elif amocrm_payment_method.installment_plan:
                payment_method = PaymentMethods.INSTALLMENT_PLAN  # рассрочка
            else:
                print("a")

            combinations.append(
                PaymentMethodCombination(
                    payment_method=payment_method,
                    maternal_capital=amocrm_payment_method.maternal_capital,
                    government_loan=amocrm_payment_method.loan,
                    housing_certificate=amocrm_payment_method.certificate,
                )
            )

        combinations.append(
            PaymentMethodCombination(
                payment_method=PaymentMethods.MORTGAGE,
                maternal_capital=False,
                government_loan=True,
                housing_certificate=False,
            )
        )
        return combinations
