from common.mixins import Choices


class CitiesTypes(Choices):
    MOSKVA: str = 'moskva', 'Москва'
    TYUMEN: str = 'toymen', 'Тюмень'
    SPB: str = 'spb', 'Санкт-Петербург'
    EKB: str = 'ekb', 'Екатеринбург'
    MO: str = 'mo', 'Московская область'


class ProjectSkyColor(Choices):
    DARK_BLUE: str = 'dark_blue', 'Синее'
    LIGHT_BLUE: str = 'light_blue', 'Голубое'
    AQUAMARINE: str = 'aquamarine', 'Аквамариновое'


class PropertyType(Choices):
    FLAT: str = "flat", "Квартира"
    PARKING: str = "parking", "Парковочное место"
    COMMERCIAL: str = "commercial", "Коммерческое помещение"
    PANTRY: str = "pantry", "Кладовка"
    COMMERCIAL_APARTMENT: str = "commercial_apartment", "Аппартаменты коммерции"


class BuildingType(Choices):
    RESIDENTIAL: str = "RESIDENTIAL", "Жилое"
    APARTMENT: str = "APARTMENT", "Апартаменты"
    PARKING: str = "PARKING", "Паркинг"
    OFFICE: str = "OFFICE", "Коммерческое"
