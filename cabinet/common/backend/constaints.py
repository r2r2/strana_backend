from common.mixins import Choices


class CitiesTypes(Choices):
    MOSKVA: str = 'moskva', 'Москва'
    TYUMEN: str = 'toymen', 'Тюмень'
    SPB: str = 'spb', 'Санкт-Петербург'
    EKB: str = 'ekb', 'Екатеринбург'
    MO: str = 'mo', 'Московская область'
