import asyncio

from boilerplates.logging import LogFormat, setup_logging

from src.core.settings import DynaconfSettings, load_settings
from src.modules.storage import StorageSettings
from src.modules.storage.service import StorageService

from .filler import DataFiller, FillerOptions, MessageFakerOptions


class FillerSettings(DynaconfSettings):
    storage: StorageSettings


setup_logging(
    log_format=LogFormat.PLAIN,
    log_level="DEBUG",
    is_sentry_enabled=False,
    spammy_loggers=["faker.factory", "faker"],
)


async def run() -> None:
    settings = load_settings(FillerSettings)
    storage = StorageService(settings=settings.storage.db)

    filler = DataFiller(
        concurrency=1,
        options=FillerOptions(
            sports_count=50,
            teams_count=50_000,
            scouts_count=5_000,
            bookmakers_count=50,
            supervisors_count=10,
            scouts_in_match_prob_distribution={
                1: 0.645,
                2: 0.096,
                3: 0.0241,
                4: 0.0095,
                5: 0.0082,
                6: 0.009,
                7: 0.0961,
                8: 0.0045,
                9: 0.0014,
            },
            scout_change_probability=0.005,
            book_scout_chats_per_match_prob_distribution={
                1: 0.85,
                2: 0.12,
                3: 0.02,
                4: 0.01,
            },
            prob_to_another_book_to_join_chat_as_reader={
                1: 0.1,
                2: 0.3,
                3: 0.05,
            },
            prob_of_match_ticket_to_be_created=0.05,
            prob_of_ticket_to_be_returned=0.15,
            avg_msg_count_in_match_chat=25,
            avg_msg_count_in_ticket_chat=35,
            message_faker=MessageFakerOptions(
                words_in_message=70,
                prob_of_image=0.05,
            ),
        ),
        storage=storage,
    )

    await storage.start()

    try:
        await filler.fill(
            iterations=100,
            start_from=10,
        )

    finally:
        await storage.stop()


asyncio.run(run())
