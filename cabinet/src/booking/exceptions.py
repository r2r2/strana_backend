from http import HTTPStatus

from .entities import BaseBookingException


class BookingWrongStepError(BaseBookingException):
    message: str = "Неверный шаг бронирования."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_wrong_step"


class BookingNotFoundError(BaseBookingException):
    message: str = "Бронирование не найдено."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "booking_not_found"


class BookingWrongPipelineIDError(BaseBookingException):
    message: str = "Воронка не участвует в логике ЛК."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_wrong_pipeline_id"


class BookingTimeOutError(BaseBookingException):
    message: str = "Время бронирования истекло."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_time_out"


class BookingTimeOutRepeatError(BaseBookingException):
    message: str = "Время бронирования истекло."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_time_out_repeat"


class BookingPropertyMissingError(BaseBookingException):
    message: str = "Объект бронирования не найден."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_property_missing"


class BookingTypeMissingError(BaseBookingException):
    message: str = "Тип бронирования не найден."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_type_missing"


class BookingOnlinePaymentError(BaseBookingException):
    message: str = "Ошибка онлайн оплаты."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_payment_failed"


class BookingUnknownReasonError(BaseBookingException):
    message: str = "Неизвестная ошибка бронирования."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_unknown_reason"


class BookingPropertyUnavailableError(BaseBookingException):
    def __init__(self, booked: bool, in_deal: bool) -> None:
        self.message = f"Объект недвижимости недоступен. booked={booked}, in_deal={in_deal}"

    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_property_unavailable"


class BookingUnfinishedExistsError(BaseBookingException):
    message: str = "Есть незавершенное бронирование."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_unfinished_exists"


class BookingRedirectFailError(BaseBookingException):
    message: str = "Ошибка перенаправления бронирования."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_redirect_fail"


class BookingResourceNotFound(BaseBookingException):
    message: str = "Ресурс не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "booking_resource_missing"


class BookingWebhookFatalError(BaseBookingException):
    message: str = "Ошибка вебхука."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_webhook_fatal"


class BookingAlreadyEmailedError(BaseBookingException):
    message: str = "Письмо уже было отправлено."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_already_emailed"


class BookingUserInactiveError(BaseBookingException):
    message: str = "Почта не подтверждена."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_user_inactive"


class BookingForbiddenError(BaseBookingException):
    message: str = "Объект не может быть забронирован"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_forbidden"


class BookingChargeReachedError(BaseBookingException):
    message: str = "Превышено значение комиссии."
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_charge_reached"


class BookingRequestValidationError(BaseBookingException):
    def __init__(self, message: str = "booking_request_validation") -> None:
        self.message = message

    status: int = HTTPStatus.UNPROCESSABLE_ENTITY
    reason: str = "booking_unprocessable_entity"


class BookingPaymentMethodNotFoundError(BaseBookingException):
    message = "Указанная комбинация данных для способа покупки не может быть использована"
    status: int = HTTPStatus.BAD_REQUEST
    reason: str = "booking_payment_method_not_found_error"


class BookingBadRequestError(BaseBookingException):
    def __init__(self, message: str = "booking_bad_request") -> None:
        self.message = message

    status = HTTPStatus.BAD_REQUEST
    reason = "booking_bad_request"


class BookingBadFileError(BaseBookingException):
    def __init__(self, message: str = "booking_request_bad_file") -> None:
        self.message = message

    status = HTTPStatus.UNPROCESSABLE_ENTITY
    reason = "booking_bad_file"


class BookingPurchaseHelpTextNotFound(BaseBookingException):
    message = "Текст не был найден"
    status = HTTPStatus.NOT_FOUND
    reason = "booking_purchase_help_text_not_found"


class BookingIdWasNotFoundError(BookingWebhookFatalError):
    message = "Ошибка вебхука; id не найдено"


class BookingReservationMatrixNotFoundError(BaseBookingException):
    message = "Матрица бронирования не найдена"
    status = HTTPStatus.NOT_FOUND
    reason = "booking_reservation_matrix_not_found"


class BookingHasNoCorrectFixationTaskError(BaseBookingException):
    message = "Бронирование не имеет корректной задачи для продления фиксации клиента"
    status = HTTPStatus.NOT_FOUND
    reason = "booking_has_no_correct_fixation_task"
