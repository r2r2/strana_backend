from pydantic import BaseModel


class NewTicketTgNotificationPayload(BaseModel):
    ticket_id: int
    match_id: int | None
    chat_id: int
    created_by: str
