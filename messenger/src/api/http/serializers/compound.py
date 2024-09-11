from pydantic import BaseModel

from src.api.http.serializers.chats import ChatUnreadCountersResponse
from src.api.http.serializers.tickets import TicketUnreadCountersResponse


class CompoundCountersResponse(BaseModel):
    chats: ChatUnreadCountersResponse
    tickets: TicketUnreadCountersResponse
