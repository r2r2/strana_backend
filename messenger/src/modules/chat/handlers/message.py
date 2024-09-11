import base64
from typing import Any

from sl_messenger_protobuf.enums_pb2 import MessageSendFailedErrorCode
from sl_messenger_protobuf.requests_pb2 import SendMessageCommand
from sl_messenger_protobuf.responses_pb2 import MessageSendFailedUpdate, MessageSentUpdate

from src.controllers.permissions import PermissionsController
from src.core.types import UserId
from src.entities.messages import MAX_MESSAGE_LENGTH
from src.exceptions import (
    ConnectionClosedError,
    MessageValidationError,
    NotPermittedError,
)
from src.modules.chat.handlers.base import BaseMessageHandler, handler_for
from src.modules.service_updates.entities import MessageSentToChat


@handler_for(SendMessageCommand)
class MessageHandler(BaseMessageHandler[SendMessageCommand]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.cached_check_permissions = self._cacher.cached_func(
            self._check_permissions,
            ttl=600,
            noself=True,
        )

    async def __call__(self, message: SendMessageCommand) -> None:
        try:
            async with self.storage.connect(autocommit=True) as storage_conn:
                chat_version = await storage_conn.chats.get_chat_version(chat_id=message.chat_id)

                # Check permissions
                is_permitted, error_msg = await self.cached_check_permissions(
                    user_id=self.connection.user_id,
                    chat_id=message.chat_id,
                    chat_version=chat_version,
                )
                if not is_permitted:
                    raise NotPermittedError(message=error_msg)

                await self._validate_message(message_command=message)

                # Save message to storage
                stored_message = await storage_conn.messages.create_message(
                    sender_id=self.connection.user_id,
                    chat_id=message.chat_id,
                    content=message.content,
                    reply_to=message.replied_msg_id if message.replied_msg_id else None,
                )

            # Publish to service updates
            await self.updates_publisher.publish_update(
                MessageSentToChat(
                    cid=self.connection.cid,
                    message_id=stored_message.id,
                    chat_id=message.chat_id,
                    content_raw=base64.b64encode(message.content.SerializeToString()).decode(),
                    sender_id=self.connection.user_id,
                    initiator_id=self.connection.user_id,
                    msg_created_at=int(stored_message.created_at.timestamp()),
                    do_not_increment_counter=False,
                ),
            )

            # Confirm that message was saved
            await self.connection.transport.send_message(
                MessageSentUpdate(temporary_id=message.temporary_id, message_id=stored_message.id),
            )

        except ConnectionClosedError:
            raise

        except MessageValidationError as exc:
            await self.connection.transport.send_message(
                MessageSendFailedUpdate(
                    temporary_id=message.temporary_id,
                    error_code=MessageSendFailedErrorCode.MESSAGE_SEND_FAILED_ERROR_CODE_VALIDATION_ERROR,
                    error_message=exc.message,
                ),
            )

        except NotPermittedError as exc:
            await self.connection.transport.send_message(
                MessageSendFailedUpdate(
                    temporary_id=message.temporary_id,
                    error_code=MessageSendFailedErrorCode.MESSAGE_SEND_FAILED_ERROR_CODE_NOT_PERMITTED,
                    error_message=exc.message,
                ),
            )

        except Exception as exc:  # pylint: disable=broad-except
            self.logger.error(f"Unknown error occured: {type(exc).__name__}", exc_info=True)
            self.connection.transport.stats.on_server_error()
            await self.connection.transport.send_message(
                MessageSendFailedUpdate(
                    temporary_id=message.temporary_id,
                    error_code=MessageSendFailedErrorCode.MESSAGE_SEND_FAILED_ERROR_CODE_UNSPECIFIED,
                    error_message="Cannot process message, please try again later",
                ),
            )

    async def _check_permissions(
        self,
        user_id: UserId,
        chat_id: int,
        chat_version: int | None,  # for cache invalidation
    ) -> tuple[bool, str | None]:
        async with self.storage.connect() as storage:
            controller = PermissionsController()
            return await controller.is_chat_writable_by_user(
                chat_id=chat_id,
                user_id=user_id,
                storage=storage,
            )

    async def _validate_message(self, message_command: SendMessageCommand) -> None:
        content = message_command.content
        content_type = content.WhichOneof("content")
        match content_type:
            case "text":
                if len(content.text.text) > MAX_MESSAGE_LENGTH:
                    raise MessageValidationError(f"Maximum message length - {MAX_MESSAGE_LENGTH} characters")

            case "file":
                async with self.storage.connect() as db:
                    file = await db.file_uploads.get_uploaded_file(content.file.file_id)
                    if not file:
                        raise MessageValidationError("File not found")

                    message_command.content.file.filename = file.filename
                    message_command.content.file.size = file.byte_size
                    message_command.content.file.mime_type = file.mime_type

            case _:
                raise MessageValidationError(f"Unsupported message content type: {content_type}")
