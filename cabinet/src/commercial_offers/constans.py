from enum import StrEnum


class OfferConstants(StrEnum):
    """
    Типы корпусов для запроса
    """
    OFFER_SOURCE: str = "panel_manager"
    TILDA_TEMPLATE_URL: str = "https://strana1.tilda.ws/comoffer"
    TILDA_TEMPLATE_SITE_ID: str = "5959914"
    TILDA_TEMPLATE_PAGE_ID: str = "40916280"