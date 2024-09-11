import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import timedelta
from random import choice, random, randrange
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock

from faker import Faker
from sl_messenger_protobuf.messages_pb2 import MessageContent as MessageContentPb
from sl_messenger_protobuf.messages_pb2 import TextContent as TextContentPb

from src.controllers.matches import MatchesController
from src.controllers.messages import MessagesController
from src.controllers.permissions import PermissionsController
from src.controllers.tickets import TicketsController
from src.entities.matches import MatchDataWithState, MatchScoutData, MatchState, MatchTeamData
from src.entities.messages import DeliveryStatus
from src.entities.tickets import TicketCloseReason
from src.entities.users import AuthPayload, Language, Role
from src.modules.storage import StorageServiceProto
from src.modules.storage.models import Sport, User
from src.modules.storage.service import Storage
from src.providers.time import datetime_now


async def clean_table(table: Any, session: Storage) -> None:
    from sqlalchemy import delete

    query = delete(table)
    await session._session.execute(query)
    await session.commit_transaction()


def triggered(probability: float) -> bool:
    return random() < probability  # noqa: S311


def rndavg(avg: int) -> int:
    return randrange(1, avg * 2)


def determine_prob(prob_distribution: dict[int, float]) -> int | None:
    for value, prob in sorted(prob_distribution.items(), reverse=True, key=lambda x: x[1]):
        if triggered(prob):
            return value

    return None


@dataclass
class MessageFakerOptions:
    words_in_message: int
    prob_of_image: float


@dataclass
class PerfStats:
    exec_times: set[float]


class PerfCounter:
    def __init__(self) -> None:
        self._stats = dict[str, PerfStats]()

    @asynccontextmanager
    async def measure(self, metric: str) -> AsyncGenerator[None, None]:
        tstart = time.perf_counter()
        yield
        tend = time.perf_counter()
        self._stats.setdefault(metric, PerfStats(exec_times=set())).exec_times.add(tend - tstart)

    def pop_stats(self, prefix: str = "") -> None:
        for metric, stats in self._stats.items():
            max_time = max(stats.exec_times)
            min_time = min(stats.exec_times)
            avg_time = sum(stats.exec_times) / len(stats.exec_times)
            print(f"{prefix}{metric}: {avg_time:.4f} (min: {min_time:.4f}, max: {max_time:.4f})")

        self._stats.clear()

    def __del__(self) -> None:
        if self._stats:
            self.pop_stats()


@dataclass
class FillerOptions:
    sports_count: int
    teams_count: int
    scouts_count: int
    bookmakers_count: int
    supervisors_count: int
    scouts_in_match_prob_distribution: dict[int, float]
    scout_change_probability: float
    book_scout_chats_per_match_prob_distribution: dict[int, float]
    prob_to_another_book_to_join_chat_as_reader: dict[int, float]
    prob_of_match_ticket_to_be_created: float
    prob_of_ticket_to_be_returned: float
    avg_msg_count_in_match_chat: int
    avg_msg_count_in_ticket_chat: int

    message_faker: MessageFakerOptions


class MessageFaker:
    def __init__(self, options: MessageFakerOptions, provider: Faker) -> None:
        self.options = options
        self.provider = provider

    def get_fake_message(self) -> MessageContentPb:
        return MessageContentPb(text=TextContentPb(text=self.provider.text(max_nb_chars=100)))


class TicketActivityFaker:
    def __init__(
        self,
        ticket_id: int,
        author_id: int,
        super_id: int,
    ) -> None:
        self.ticket_id = ticket_id
        self.author_id = author_id
        self.super_id = super_id


class DataFiller:
    def __init__(
        self,
        concurrency: int,
        options: FillerOptions,
        storage: StorageServiceProto,
    ) -> None:
        self.concurrency = concurrency
        self.options = options
        self.storage = storage
        self.faker = Faker()
        self.message_faker = MessageFaker(options.message_faker, self.faker)
        self.perf = PerfCounter()

    async def prefill_sports(self) -> None:
        async with self.storage.connect(autocommit=False) as db:
            from sqlalchemy import insert

            await clean_table(Sport, db)  # type: ignore

            for idx in range(self.options.sports_count):
                query = insert(Sport).values(
                    id=idx + 1,
                    name_ru=self.faker.text(max_nb_chars=35),
                    name_en=self.faker.text(max_nb_chars=35),
                    created_at=datetime_now(),
                )
                await db._session.execute(query)  # type: ignore

            await db.commit_transaction()

    async def prefill_users(self) -> None:
        async with self.storage.connect(autocommit=False) as db:
            await clean_table(User, db)  # type: ignore

            for idx in range(self.options.bookmakers_count):
                await db.users.create(
                    user_id=1_000_000 + idx,
                    name=self.faker.text(max_nb_chars=35),
                    scout_number=None,
                    role=Role.BOOKMAKER,
                )

            for idx in range(self.options.supervisors_count):
                await db.users.create(
                    user_id=2_000_000 + idx,
                    name=self.faker.text(max_nb_chars=35),
                    scout_number=None,
                    role=Role.SUPERVISOR,
                )

            for idx in range(self.options.scouts_count):
                await db.users.create(
                    user_id=idx,
                    name=self.faker.text(max_nb_chars=35),
                    scout_number=idx,
                    role=Role.SCOUT,
                )

            await db.commit_transaction()

    async def _create_chat(
        self,
        book_id: int,
        scout_id: int,
        match_id: int,
    ) -> None:
        async with self.storage.connect(autocommit=False) as db:
            controller = MatchesController(
                presence_service=AsyncMock(),
                rabbitmq_publisher=AsyncMock(),
                sportlevel=AsyncMock(),
                storage=db,
                permissions=PermissionsController(),
                messages=MessagesController(
                    storage=db,
                    rabbitmq_publisher=AsyncMock(),
                ),
                unread_counters=AsyncMock(),
            )

            result = await controller.start_chat(
                match_id=match_id,
                user=AuthPayload(
                    id=book_id,
                    roles=[Role.BOOKMAKER],
                    abilities=[],
                    lang=Language.EN,
                ),
                scout_user_id=scout_id,
            )

            chat_id = result.chat_id

            messages_count = rndavg(self.options.avg_msg_count_in_match_chat)

            msg_id = 9_999_999
            for idx in range(1, messages_count):
                sender_id = book_id if idx % 2 == 0 else scout_id

                msg = await db.messages.create_message(
                    sender_id=sender_id, chat_id=chat_id, content=self.message_faker.get_fake_message()
                )
                msg_id = msg.id

            last_read_by_book = msg_id if triggered(0.5) else msg_id - randrange(1, max(messages_count, 2))
            last_read_by_scout = msg_id if triggered(0.5) else msg_id - randrange(1, max(messages_count, 2))

            await db.messages.update_message_status(
                chat_id=chat_id,
                message_id=last_read_by_book,
                user_id=book_id,
                new_status=DeliveryStatus.READ,
                update_for_all=True,
            )
            await db.messages.update_message_status(
                chat_id=chat_id,
                message_id=last_read_by_scout,
                user_id=scout_id,
                new_status=DeliveryStatus.READ,
                update_for_all=True,
            )

            await db.commit_transaction()

    async def _create_ticket(self, match_id: int, created_by_id: int, created_by_role: Role) -> None:
        async with self.storage.connect(autocommit=False) as db:
            controller = TicketsController(
                rabbitmq_publisher=AsyncMock(),
                presence_service=AsyncMock(),
                storage=db,
                messages=MessagesController(
                    storage=db,
                    rabbitmq_publisher=AsyncMock(),
                ),
                unread_counters=AsyncMock(),
            )

            user_auth = AuthPayload(
                id=created_by_id,
                roles=[created_by_role],
                abilities=[],
                lang=Language.EN,
            )

            response = await controller.create_ticket(
                user=user_auth,
                match_id=match_id,
                created_from_chat_id=None,
                message="",
            )

            ticket_id = response.ticket_id

            ticket = await db.tickets.get_ticket_by_id(ticket_id=ticket_id)
            assert ticket is not None

            random_supervisor = randrange(2_000_000, 2_000_000 + self.options.supervisors_count)
            supervisor_auth = AuthPayload(
                id=random_supervisor,
                roles=[Role.SUPERVISOR],
                abilities=[],
                lang=Language.EN,
            )

            await controller.take_into_work(ticket=ticket, user=supervisor_auth)

            messages_count = rndavg(self.options.avg_msg_count_in_ticket_chat)

            last_msg_id = 0
            for idx in range(1, messages_count):
                sender_id = random_supervisor if idx % 2 == 0 else created_by_id

                msg = await db.messages.create_message(
                    sender_id=sender_id, chat_id=ticket.chat_id, content=self.message_faker.get_fake_message()
                )
                last_msg_id = msg.id

            await controller.close_ticket(
                ticket=ticket,
                user=supervisor_auth,
                comment=self.faker.text(max_nb_chars=200),
                close_reason=choice(list(TicketCloseReason)),
            )

            if triggered(self.options.prob_of_ticket_to_be_returned):
                await controller.reopen_ticket(ticket=ticket, user=user_auth)
                messages_count = rndavg(self.options.avg_msg_count_in_ticket_chat // 2)
                for idx in range(1, messages_count):
                    sender_id = random_supervisor if idx % 2 == 0 else created_by_id

                    msg = await db.messages.create_message(
                        sender_id=sender_id, chat_id=ticket.chat_id, content=self.message_faker.get_fake_message()
                    )
                    last_msg_id = msg.id

                await controller.close_ticket(
                    ticket=ticket,
                    user=supervisor_auth,
                    comment=self.faker.text(max_nb_chars=200),
                    close_reason=choice(list(TicketCloseReason)),
                )

            await controller.confirm_ticket(ticket=ticket, user=user_auth)

            last_read_by_user = last_msg_id if triggered(0.5) else last_msg_id - randrange(1, max(messages_count, 2))
            last_read_by_super = last_msg_id if triggered(0.5) else last_msg_id - randrange(1, max(messages_count, 2))

            await db.messages.update_message_status(
                chat_id=ticket.chat_id,
                message_id=last_read_by_user,
                user_id=user_auth.id,
                new_status=DeliveryStatus.READ,
                update_for_all=True,
            )
            await db.messages.update_message_status(
                chat_id=ticket.chat_id,
                message_id=last_read_by_super,
                user_id=supervisor_auth.id,
                new_status=DeliveryStatus.READ,
                update_for_all=True,
            )
            await db.commit_transaction()

    async def create_single_match(self, match_id: int) -> None:
        scouts_count = determine_prob(self.options.scouts_in_match_prob_distribution)

        match_info = MatchDataWithState(
            start_at=datetime_now(),
            finish_at=datetime_now() + timedelta(minutes=randrange(90, 360)),
            sport_id=randrange(1, self.options.sports_count),
            team_a=MatchTeamData(
                id=randrange(1, self.options.teams_count),
                name_en=self.faker.text(max_nb_chars=35),
                name_ru=self.faker.text(max_nb_chars=35),
            ),
            team_b=MatchTeamData(
                id=randrange(1, self.options.teams_count),
                name_en=self.faker.text(max_nb_chars=35),
                name_ru=self.faker.text(max_nb_chars=35),
            ),
            sportlevel_id=match_id,
            scouts=[],
            state=MatchState.ACTIVE,
        )

        async with self.storage.connect(autocommit=False) as db:
            async with self.perf.measure("Insert match"):
                await db.matches.create_match_with_scouts(match_data=match_info)

            scouts: list[MatchScoutData] = []

            if scouts_count is not None:
                uq_scouts = set()
                for idx in range(scouts_count):
                    while (scout_id := randrange(1, self.options.scouts_count)) in uq_scouts:
                        ...

                    uq_scouts.add(scout_id)

                    scouts.append(
                        MatchScoutData(
                            id=scout_id,
                            scout_number=scout_id,
                            is_main_scout=idx == 0,
                            name=self.faker.text(max_nb_chars=35),
                        )
                    )

            scout_ids = [scout.id for scout in scouts]

            async with self.perf.measure("Insert scouts"):
                await db.matches.set_match_scouts(match_id=match_id, scouts=scouts)

            async with self.perf.measure("Commit match + scouts"):
                await db.commit_transaction()

        if not scout_ids:
            return

        chats_count = determine_prob(self.options.book_scout_chats_per_match_prob_distribution)
        if chats_count:
            used_books = set()
            for _ in range(chats_count):
                while (random_book := randrange(1_000_000, 1_000_000 + self.options.bookmakers_count)) in used_books:
                    ...

                used_books.add(random_book)
                random_scout = choice(scout_ids)

                async with self.perf.measure("Create chat book - scout"):
                    await self._create_chat(
                        book_id=random_book,
                        scout_id=random_scout,
                        match_id=match_id,
                    )

        if triggered(self.options.prob_of_match_ticket_to_be_created):
            async with self.perf.measure("Create ticket"):
                await self._create_ticket(
                    match_id=match_id,
                    created_by_id=randrange(1_000_000, 1_000_000 + self.options.bookmakers_count),
                    created_by_role=Role.BOOKMAKER,
                )

    async def fill(self, iterations: int, start_from: int) -> None:
        if self.concurrency == 1:
            await self.prefill_sports()
            await self.prefill_users()

            for idx, match_id in enumerate(range(1 + start_from, 1 + start_from + iterations)):
                async with self.perf.measure("create_single_match"):
                    await self.create_single_match(match_id=match_id)

                if idx % 100 == 0:
                    self.perf.pop_stats(prefix=f"#{idx} ")

        else:
            for match_id in range(1 + start_from, 1 + start_from + iterations, self.concurrency):
                tasks: list[asyncio.Task[Any]] = []
                for idx in range(self.concurrency):
                    tasks.append(asyncio.create_task(self.create_single_match(match_id=match_id + idx)))

                result = await asyncio.gather(*tasks, return_exceptions=True)
                for res in result:
                    if isinstance(res, Exception):
                        raise res
