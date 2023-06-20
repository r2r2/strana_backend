from jinja2 import Template
from aiofile import async_open
from config import email_config
from typing import Optional, Any, Union, Type
from asyncio import ensure_future, Future, create_task, Task
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, errors
from tortoise import Tortoise
from copy import copy

from config import tortoise_config

from .repos import LogEmailRepo, LogEmail


class EmailService(object):
    """
    Email sender implementation
    """

    def __init__(
        self,
        topic: str,
        recipients: list[str],
        subtype: str = "html",
        retries: Optional[int] = 5,
        content: Optional[str] = None,
        template: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        lk_type: Optional[str] = None,
        mail_event_slug: Optional[str] = None,
    ) -> None:
        self._topic: str = topic
        self._subtype: str = subtype
        self._retries: int = retries
        self._current_try: int = 1
        self._recipients: list[str] = [email for email in recipients if email]
        self.lk_type: Optional[str] = lk_type
        self.mail_event_slug: Optional[str] = mail_event_slug
        self.log_email_repo: LogEmailRepo = LogEmailRepo()
        self.orm_class: Type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        if not content and not (context and template):
            raise ValueError(
                "You must specify either email content or provide context and template to render it."
            )
        if content and context:
            raise ValueError("You must specify one of content or template with context")

        self._content: Union[str, None] = content
        self._template: Union[str, None] = template
        self._context: Union[dict[str, Any], None] = context

        self._config: ConnectionConfig = ConnectionConfig(
            MAIL_USERNAME=email_config["username"],
            MAIL_PASSWORD=email_config["password"],
            MAIL_FROM=email_config["sender"],
            MAIL_PORT=email_config["port"],
            MAIL_SERVER=email_config["host"],
            MAIL_TLS=email_config["use_tls"],
            MAIL_SSL=email_config["use_ssl"],
            USE_CREDENTIALS=email_config["use_cred"],
        )

    def as_future(self) -> Future:
        """
        Wrap into a future object
        """
        return ensure_future(self())

    def as_task(self) -> Task:
        """
        Wrap into a task object
        """
        return create_task(self())

    async def __call__(self) -> None:
        """
        Logic execution
        """
        if len(self._recipients) == 0:
            return

        sender: FastMail = FastMail(self._config)
        message: MessageSchema = await self.make_message()

        log_email = await self._loging_email(is_sent=True, message=message)

        try:
            await sender.send_message(message=message)
        except errors.ConnectionErrors:
            await self._retry(sender=sender, message=message, log_email=log_email)

    async def make_message(self) -> MessageSchema:
        message_args = dict(subject=self._topic, subtype=self._subtype, recipients=self._recipients)
        if self._content:
            body: str = self._content
            message_args['body'] = body
        else:
            async with async_open(self._template, "r") as file:
                html: str = await file.read()
            body: str = await Template(html, enable_async=True).render_async(**self._context)
            message_args['html'] = body
        return MessageSchema(**message_args)

    async def _retry(
        self,
        sender: FastMail,
        message: MessageSchema,
        log_email: LogEmail,
    ) -> None:
        self._current_try += 1
        try:
            await sender.send_message(message=message)
        except Exception:
            if self._current_try < self._retries:
                await self._retry(sender=sender, message=message, log_email=log_email)
            else:
                await self.log_email_repo.update(model=log_email, data=dict(is_sent=False))

    async def _loging_email(self, is_sent: bool, message: MessageSchema) -> LogEmail:
        """
        Логируем отправленное письмо в админке через селери таску.
        """
        data = dict(
            topic=self._topic,
            text=self._content if self._content else message.html,
            lk_type=self.lk_type,
            mail_event_slug=self.mail_event_slug,
            recipient_emails=", ".join(self._recipients),
            is_sent=is_sent,
        )
        return await self.log_email_repo.create(data=data)
