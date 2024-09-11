import base64

from sl_messenger_protobuf.enums_pb2 import ErrorReason
from sl_messenger_protobuf.requests_pb2 import DeleteMessageCommand, EditMessageCommand
from sl_messenger_protobuf.responses_pb2 import ErrorOccuredUpdate

from src.controllers.permissions import PermissionsController
from src.core.types import ProtobufMessageT, UserId
from src.exceptions import MessageValidationError, NotPermittedError
from src.modules.chat.handlers import BaseMessageHandler, handler_for
from src.modules.chat.handlers.utils import validate_message
from src.modules.service_updates.entities import MessageDeleted, MessageEdited
from src.modules.storage import StorageProtocol
from src.modules.storage.models import Message
from src.providers.time import datetime_now


class BaseMessageUpdate(BaseMessageHandler[ProtobufMessageT]):
    async def handle_message(self, message_command: ProtobufMessageT) -> None:
        raise NotImplementedError

    async def process_message_update(self, message: ProtobufMessageT) -> None:
        try:
            await self.handle_message(message)
        except (MessageValidationError, NotPermittedError) as e:
            await self.connection.transport.send_message(
                ErrorOccuredUpdate(
                    reason=ErrorReason.ERROR_REASON_CLIENT,
                    description=e.message,
                ),
            )
        except Exception as exc:  # pylint: disable=broad-except
            self.logger.error(f"Unknown error occured: {type(exc).__name__}", exc_info=True)
            self.connection.transport.stats.on_server_error()
            await self.connection.transport.send_message(
                ErrorOccuredUpdate(
                    reason=ErrorReason.ERROR_REASON_SERVER,
                    description="Cannot process message, please try again later",
                ),
            )

    async def _check_permissions(
        self,
        user_id: UserId,
        message_id: int,
        storage_conn: StorageProtocol,
    ) -> tuple[bool, Message | None]:
        controller = PermissionsController()
        return await controller.check_message_edit_permissions(
            user_id=user_id,
            message_id=message_id,
            storage=storage_conn,
        )


@handler_for(EditMessageCommand)
class EditMessageHandler(BaseMessageUpdate[EditMessageCommand]):
    async def __call__(self, message_command: EditMessageCommand) -> None:
        await self.process_message_update(message_command)

    async def handle_message(self, message_command: EditMessageCommand) -> None:
        async with self.storage.connect(autocommit=True) as storage_conn:
            # Check permissions
            is_permitted, db_message = await self._check_permissions(
                user_id=self.connection.user_id,
                message_id=message_command.message_id,
                storage_conn=storage_conn,
            )
            if not db_message:
                return
            if not is_permitted:
                raise NotPermittedError(message="You are not permitted to edit this message")

            await validate_message(message_command=message_command)

            # Update message in storage
            await storage_conn.messages.update_message(
                message=db_message,
                update_data={"content": message_command.content.SerializeToString()},
            )

        # Publish to service updates
        await self.updates_publisher.publish_update(
            MessageEdited(
                cid=self.connection.cid,
                message_id=message_command.message_id,
                chat_id=message_command.chat_id,
                content_raw=base64.b64encode(message_command.content.SerializeToString()).decode(),
            ),
        )


@handler_for(DeleteMessageCommand)
class DeleteMessageHandler(BaseMessageUpdate[DeleteMessageCommand]):
    async def __call__(self, message_command: DeleteMessageCommand) -> None:
        await self.process_message_update(message_command)

    async def handle_message(self, message_command: DeleteMessageCommand) -> None:
        async with self.storage.connect(autocommit=True) as storage_conn:
            # Check permissions
            is_permitted, db_message = await self._check_permissions(
                user_id=self.connection.user_id,
                message_id=message_command.message_id,
                storage_conn=storage_conn,
            )
            if not db_message:
                return
            if not is_permitted:
                raise NotPermittedError(message="You are not permitted to delete this message")

            # Delete message from storage
            await storage_conn.messages.update_message(
                message=db_message,
                update_data={"deleted_at": datetime_now()},
            )

        # Publish to service updates
        await self.updates_publisher.publish_update(
            MessageDeleted(
                cid=self.connection.cid,
                message_id=message_command.message_id,
                chat_id=message_command.chat_id,
            ),
        )
