from dataclasses import dataclass


@dataclass
class ChatAccessDTO:
    is_accessible: bool
    error_msg: str | None = None
    last_available_message_id: int | None = None
    first_available_message_id: int | None = None
