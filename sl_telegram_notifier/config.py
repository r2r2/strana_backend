from pydantic import BaseModel, SecretStr


class TelegramNotifierConfig(BaseModel):
    token: SecretStr
    chat_id: int
    max_message_length: int = 4000
    is_enabled: bool = False
