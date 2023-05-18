from common.files.validations import UploadedFileValidation
from src.booking.exceptions import BookingBadFileError


class DDUUploadFileValidator(UploadedFileValidation):
    exception_class = BookingBadFileError
