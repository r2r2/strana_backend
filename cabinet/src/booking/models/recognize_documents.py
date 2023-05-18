from typing import Optional

from src.booking.entities import BaseBookingModel


class ResponseRecognizeDocumentsModel(BaseBookingModel):
    """
    Ответ на запрос распознавания документов в БАЗИС-е
    """

    success: bool
    task_id: Optional[str]
