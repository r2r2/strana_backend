from sl_messenger_protobuf.enums_pb2 import ChatCloseReason
from sl_messenger_protobuf.messages_pb2 import ChatClosedNotificationContent, MessageContent

from src.controllers.messages import MessagesController
from src.core.types import ConnectionId
from src.entities.matches import ChatType, MatchScoutData
from src.entities.users import Role
from src.modules.service_updates.entities import MatchScoutsChanged
from src.modules.service_updates.handlers.base import BaseUpdateHandler


class MatchScoutsChangedUpdateHandler(BaseUpdateHandler[MatchScoutsChanged], update_type=MatchScoutsChanged):
    async def handle(self, cid: ConnectionId | None, update: MatchScoutsChanged) -> None:
        async with self.storage_srvc.connect(autocommit=True) as db:
            current_match_scouts = await db.matches.get_match_scouts(match_id=update.sportlevel_id)
            current_main_scout = next((scout for scout in current_match_scouts if scout.is_main_scout), None)
            new_main_scout = next((scout for scout in update.scouts if scout.is_main_scout), None)
            await db.matches.set_match_scouts(match_id=update.sportlevel_id, scouts=update.scouts)

        if current_main_scout != new_main_scout:
            await self._process_changed_main_scout(
                match_id=update.sportlevel_id,
                current_main_scout=current_main_scout,
                new_main_scout=new_main_scout,
            )

        if new_main_scout:
            await self._try_process_new_user_as_main_scout(main_scout=new_main_scout)

    async def _process_changed_main_scout(
        self,
        match_id: int,
        current_main_scout: MatchScoutData | None,
        new_main_scout: MatchScoutData | None,
    ) -> None:
        async with self.storage_srvc.connect(autocommit=False) as storage:
            messages_controller = MessagesController(
                storage=storage,
                rabbitmq_publisher=self.rabbitmq_publisher,
            )
            chats = await storage.chats.get_all_chats_by_match(
                match_id=match_id,
                chat_types=[ChatType.MATCH],
            )
            active_chats = [chat for chat in chats if not chat.is_closed]
            for chat in active_chats:
                message = await messages_controller.create_message(
                    chat_id=chat.id,
                    content=MessageContent(
                        chat_closed_notification=ChatClosedNotificationContent(
                            reason=ChatCloseReason.CHAT_CLOSE_REASON_MATCH_SCOUT_IS_CHANGED,
                        ),
                    ),
                    initiator_id=None,
                )
                if current_main_scout:
                    await storage.chats.update_scout_membership(
                        chat_id=chat.id,
                        scout_id=current_main_scout.id,
                        last_available_message_id=message.id,
                        is_archive_member=True,
                        has_write_permission=False,
                    )
                if new_main_scout:
                    await storage.chats.update_scout_membership(
                        chat_id=chat.id,
                        scout_id=new_main_scout.id,
                        first_available_message_id=message.id,
                    )

            await storage.commit_transaction()

    async def _try_process_new_user_as_main_scout(
        self,
        main_scout: MatchScoutData,
    ) -> None:
        async with self.storage_srvc.connect(autocommit=False) as storage:
            user = await storage.users.get_by_id(user_id=main_scout.id)
            if user:
                # User is found in the database, nothing to do
                return

            await storage.users.create(
                user_id=main_scout.id, name=main_scout.name, scout_number=main_scout.scout_number, role=Role.SCOUT
            )
