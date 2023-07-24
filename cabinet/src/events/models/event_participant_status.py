from ..entities import BaseEventModel


class RequestEventAdminModel(BaseEventModel):
    """
    Модель запроса для апи отправки агенту письма об участии в мероприятии при добавлении в админке.
    """
    agent_id: int
    event_id: int
    agent_status: str
