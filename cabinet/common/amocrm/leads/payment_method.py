from dataclasses import dataclass
from typing import TypedDict


@dataclass(frozen=True, eq=True)
class AmoCRMPaymentMethod:
    """
    Общая логика: есть поле в AMOCRM которому присуждается определённое значение
    айдишник этого поля: 366639
    значение: айдишник уникального сочетания методов оплаты и описания
    """
    cash: bool = False
    mortgage: bool = False
    installment_plan: bool = False

    maternal_capital: bool = False
    certificate: bool = False
    loan: bool = False

    @property
    def to_amocrm(self) -> "AmoEnumValueDict":
        return AmoCRMPaymentMethodMapping[self]


class AmoEnumValueDict(TypedDict):
    """
    Меппинг данных из AMOCRM
    @param enum: int (значение записи из AMOCRM)
    @value: str (описание сочетания метода оплаты в AMOCRM)
    """
    enum: int
    value: str


AmoCRMPaymentMethodMapping: dict[AmoCRMPaymentMethod, AmoEnumValueDict] = {
    # 100% - 714853
    AmoCRMPaymentMethod(cash=True): dict(enum=714853, value="100%"),
    # ипотека - 714855
    AmoCRMPaymentMethod(mortgage=True): dict(enum=714855, value="Ипотека"),
    # наличные+мск - 714859
    AmoCRMPaymentMethod(cash=True, maternal_capital=True): dict(enum=714859, value="наличные+ МСК"),
    # рассрочка - 714861
    AmoCRMPaymentMethod(installment_plan=True): dict(enum=714861, value="Рассрочка"),
    # ипотека+мск - 1284003
    AmoCRMPaymentMethod(mortgage=True, maternal_capital=True): dict(
        enum=1284003, value="Ипотека+МСК"
    ),
    # ипотека+сертификат - 1315751
    AmoCRMPaymentMethod(mortgage=True, certificate=True): dict(
        enum=1315751, value="Ипотека +сертификат"
    ),
    # наличные+сертификат - 1315753
    AmoCRMPaymentMethod(cash=True, certificate=True): dict(
        enum=1315753, value="Наличные+сертификат"
    ),
    # наличные+сертификат+займ - 1317511
    AmoCRMPaymentMethod(cash=True, certificate=True, loan=True): dict(
        enum=1317511, value="Наличные+сертификат+займ"
    ),
    # наличные+сертификат+займ+мск - 1317551
    AmoCRMPaymentMethod(cash=True, certificate=True, loan=True, maternal_capital=True): dict(
        enum=1317551, value="Наличные+сертификат+займ+мск"
    ),
    # ипотека+займ+сертификат+МСК - 1318019
    AmoCRMPaymentMethod(mortgage=True, loan=True, certificate=True, maternal_capital=True): dict(
        enum=1318019, value="Ипотека+займ+сертификат+МСК"
    ),
    # рассрочка+мск - 1324226
    AmoCRMPaymentMethod(installment_plan=True, maternal_capital=True): dict(
        enum=1324226, value="Рассрочка+МСК"
    ),
    # Ипотека+сертификат+МСК - 1318019
    AmoCRMPaymentMethod(mortgage=True, certificate=True, maternal_capital=True): dict(
        enum=1318019, value="Ипотека+сертификат+МСК"
    ),
    # "Наличные+ипотека+сертификат+займ" - 1317513
    AmoCRMPaymentMethod(cash=True, mortgage=True, installment_plan=True, loan=True): dict(
        enum=1318019, value="Ипотека+сертификат+МСК"
    ),
}
