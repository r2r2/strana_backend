from ..entities import BaseCityModel


class CityModel(BaseCityModel):
    """
    Модель города
    """
    id: int
    name: str
    slug: str
