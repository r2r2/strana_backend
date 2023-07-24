from ..entities import BaseCityModel


class CityModel(BaseCityModel):
    """
    Модель города
    """
    id: int
    name: str
    slug: str


class CityPortalModel(BaseCityModel):
    """
    Модель города
    """
    id: str
    name: str
    slug: str
