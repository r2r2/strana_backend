import asyncio

import typer
from aioconsole import ainput
from websockets.client import connect

from src.core.logger import get_logger
from src.core.types import UserId
from src.entities.users import Language, Role
from src.entrypoints.chatclient.helpers import generate_auth_token
from src.entrypoints.chatclient.interactive import InteractiveChatClient

chatclient_cli = typer.Typer(name="Interactive chat client", no_args_is_help=True)


@chatclient_cli.command("connect", short_help="Connect to chat server")
def run_interactive_client(
    user_id: UserId = typer.Argument(...),
    host: str = typer.Option(default="localhost"),
    port: int = typer.Option(default=10000),
    autoread: bool = typer.Option(default=True),
) -> None:
    asyncio.run(
        main(
            user_id=user_id,
            host=host,
            port=port,
            autoread=autoread,
        ),
    )


async def main(
    user_id: UserId,
    host: str,
    port: int,
    autoread: bool,
) -> None:
    auth_token = generate_auth_token(user_id=user_id, roles=[Role.SUPERVISOR], lang=Language.EN, audience=["messenger"])

    async with connect(f"ws://{host}:{port}/ws/chat?token={auth_token}") as connection:
        logger = get_logger("interactive")
        logger.info(f"Using user with id: {user_id}")

        async with InteractiveChatClient(
            logger=logger,
            auth_token=auth_token,
            user_id=user_id,
            conn=connection,
            activity_interval=3.0,
            activity_auto_start=True,
            autoread=autoread,
        ) as client:
            while True:
                try:
                    command = await ainput("> ")
                    await client.handle(command)

                except (asyncio.CancelledError, KeyboardInterrupt):
                    return
