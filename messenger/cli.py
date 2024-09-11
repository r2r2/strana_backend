#!./.venv/bin/python

import typer
from boilerplates.logging import LogFormat

from src.core.logger import setup_logging
from src.core.settings import BASE_SETTINGS, LoggingSettings
from src.entrypoints.chatclient import chatclient_cli
from src.entrypoints.migrator import migrator_cli
from src.entrypoints.services import services_cli

cli = typer.Typer(no_args_is_help=True)
cli.add_typer(services_cli, name="service", short_help="Run service")
cli.add_typer(chatclient_cli, name="client", short_help="Interactive client")
cli.add_typer(migrator_cli, name="migrator", short_help="Database migrator")


@cli.callback()
def setup_cli_logging(
    log_format: LogFormat = typer.Option(default=BASE_SETTINGS.logging.log_format),
    log_level: str = typer.Option(default=BASE_SETTINGS.logging.log_level),
) -> None:
    setup_logging(
        settings=LoggingSettings(
            log_format=log_format,
            log_level=log_level.upper(),
            spammy_loggers=["alembic.ddl.postgresql", "websockets.client"],
        ),
        is_sentry_enabled=BASE_SETTINGS.sentry.is_enabled,
    )


if __name__ == "__main__":
    cli()
