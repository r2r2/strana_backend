from typing import Type, Optional, Any

import structlog

from ..repos import BookingRepo, WebhookRequestRepo
from ..types import BookingPropertyRepo, BookingRequest
from config import backend_config


class BaseBookingsService:
    """
    Кейс деактивации бронирования
    """

    query_type: str = "changePropertyStatus"
    query_name: str = "changePropertyStatus.graphql"
    query_directory: str = "/src/booking/queries/"

    def __init__(
            self,
            booking_repo: Type[BookingRepo],
            property_repo: Type[BookingPropertyRepo],
            request_class: Type[BookingRequest],
            webhook_request_repo: Type[WebhookRequestRepo],
            check_pinning: Optional[Any] = None,
            logger: Optional[Any] = structlog.getLogger(__name__),
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.property_repo: BookingPropertyRepo = property_repo()
        self.request_class: Type[BookingRequest] = request_class
        self.webhook_request_repo: WebhookRequestRepo = webhook_request_repo()
        self.check_pinning: Optional[Any] = check_pinning
        self.logger = logger

        self.login: str = backend_config["internal_login"]
        self.password: str = backend_config["internal_password"]
        self.backend_url: str = backend_config["url"] + backend_config["graphql"]
