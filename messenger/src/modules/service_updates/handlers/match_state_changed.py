from sl_messenger_protobuf.enums_pb2 import ChatCloseReason
from sl_messenger_protobuf.enums_pb2 import MatchState as MatchStatePb
from sl_messenger_protobuf.main_pb2 import ServerMessage
from sl_messenger_protobuf.messages_pb2 import ChatClosedNotificationContent, MessageContent
from sl_messenger_protobuf.responses_pb2 import MatchStateChangedUpdate

from src.controllers.messages import MessagesController
from src.core.types import ConnectionId
from src.entities.matches import ChatType
from src.modules.service_updates.entities import MatchStateChanged
from src.modules.service_updates.handlers.base import BaseUpdateHandler


class MatchStateChangedUpdateHandler(BaseUpdateHandler[MatchStateChanged], update_type=MatchStateChanged):
    async def handle(self, cid: ConnectionId | None, update: MatchStateChanged) -> None:
        async with self.storage_srvc.connect(autocommit=True) as db:
            current_state = await db.matches.get_match_by_id(sportlevel_id=update.sportlevel_id)
            if not current_state:
                dbg_method = self.logger.warning if update.new_state.is_active else self.logger.info
                dbg_method(
                    "Match not found in the database when processing state update",
                    match_id=update.sportlevel_id,
                )
                return

            old_state = current_state.state
            new_state = update.new_state

            await db.matches.update_match_state(
                sportlevel_id=update.sportlevel_id,
                state=new_state,
            )
            self.logger.debug(f"Match state updated {update.sportlevel_id}: {old_state.name} -> {new_state.name}")

            related_user_ids = await db.matches.get_all_users_related_to_match(update.sportlevel_id)
            await self._broadcast_updates(
                update=ServerMessage(
                    match_state_changed_update=MatchStateChangedUpdate(
                        match_id=update.sportlevel_id,
                        new_state=MatchStatePb.ValueType(new_state.value),
                        old_state=MatchStatePb.ValueType(old_state.value),
                    ),
                ),
                user_ids=related_user_ids,
            )

        if not new_state.is_active and old_state.is_active:
            await self._process_finished_match(match_id=update.sportlevel_id)

    async def _process_finished_match(self, match_id: int) -> None:
        self.logger.debug("Match is finished, processing related chats", match_id=match_id)

        async with self.storage_srvc.connect(autocommit=False) as storage:
            messages_controller = MessagesController(
                storage=storage,
                rabbitmq_publisher=self.rabbitmq_publisher,
            )
            chats = await storage.chats.get_all_chats_by_match(match_id=match_id)
            active_match_chats = [chat for chat in chats if not chat.is_closed and chat.chat_type == ChatType.MATCH]
            for chat in active_match_chats:
                await messages_controller.create_message(
                    chat_id=chat.id,
                    content=MessageContent(
                        chat_closed_notification=ChatClosedNotificationContent(
                            reason=ChatCloseReason.CHAT_CLOSE_REASON_MATCH_IS_CANCELLED,
                        ),
                    ),
                    initiator_id=None,
                )

            if active_match_chats:
                await storage.chats.close_chats(chat_ids=[chat.id for chat in active_match_chats])
                await storage.commit_transaction()

            if not chats:
                # If there are no chats for this match, it means that we can delete it from the database
                self.logger.info(
                    "No chats found for archived match, deleting it",
                    match_id=match_id,
                )

                await storage.matches.delete_match_with_scouts(match_id=match_id)
                await storage.commit_transaction()
