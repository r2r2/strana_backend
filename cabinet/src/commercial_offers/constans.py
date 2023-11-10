from enum import Enum

from common import mixins

class OfferConstants(str, Enum):
    """
    Типы корпусов для запроса
    """
    OFFER_SOURCE: str = "panel_manager"
