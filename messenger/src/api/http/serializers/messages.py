from pydantic import BaseModel, Field

from src.entities.matches import ChatType


class UpdateMessageRequest(BaseModel):
    content: str


class UnreadMessage(BaseModel):
    message_id: int
    chat_id: int | None = Field(None, description="сообщение из личных сообщений")
    match_id: int | None = Field(None, description="сообщение из чата по матчу")
    ticket_id: int | None = Field(None, description="сообщение из тикета")
    ticket_status: str | None = Field(None, description="статус тикета")
    chat_type: ChatType


class UnreadMessagesResponse(BaseModel):
    data: list[UnreadMessage]
    has_next_page: bool
