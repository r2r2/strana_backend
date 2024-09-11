from pydantic import BaseModel, SecretStr


class TelegramNotificationsUrlTemplates(BaseModel):
    sl_partner_match_url: str
    sl_messenger_ticket_url: str
    sl_messenger_match_ticket_url: str


class TelegramServiceSettings(BaseModel):
    api_token: SecretStr
    notifications_channel_id: int
    url_templates: TelegramNotificationsUrlTemplates
