from textwrap import dedent

from .entities import NewTicketTgNotificationPayload
from .helpers import escape_markdown_v2
from .settings import TelegramNotificationsUrlTemplates


class TelegramMessageRenderer:
    def __init__(self, url_templates: TelegramNotificationsUrlTemplates) -> None:
        self._url_templates = url_templates

    def render_new_ticket_notification_text(
        self,
        payload: NewTicketTgNotificationPayload,
    ) -> str:
        format_kwargs = payload.model_dump(mode="json")
        format_kwargs["created_by"] = escape_markdown_v2(format_kwargs["created_by"])

        if payload.match_id:
            format_kwargs["ticket_link"] = self._url_templates.sl_messenger_match_ticket_url.format(**format_kwargs)
            format_kwargs["match_link"] = self._url_templates.sl_partner_match_url.format(**format_kwargs)
            template = dedent("""
                Создана новая заявка по матчу [{match_id}]({match_link}) 
                с номером [{ticket_id}]({ticket_link}) от {created_by}\\.
            """).replace("\n", "")  # noqa: W291

        else:
            format_kwargs["ticket_link"] = self._url_templates.sl_messenger_ticket_url.format(**format_kwargs)
            template = dedent("""
                Создана новая заявка с номером [{ticket_id}]({ticket_link}) от {created_by}\\.
            """)

        return template.format(**format_kwargs)
