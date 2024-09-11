import typer
from boilerplates.logging import StructlogFormatter, generate_uvicorn_log_config
from uvicorn import run

from src.core.logger import get_logger
from src.core.settings import BASE_SETTINGS
from src.entrypoints.services.registry import SERVICES, ServiceType

services_cli = typer.Typer(no_args_is_help=True)


@services_cli.command("run", short_help="Run service")
def run_service(
    service_type: ServiceType = typer.Argument(..., case_sensitive=False),
    host: str = typer.Option(default=BASE_SETTINGS.app.host),
    port: int = typer.Option(default=BASE_SETTINGS.app.port),
    ws_ping_interval: float = typer.Option(default=BASE_SETTINGS.app.ws_ping_interval),
    ws_ping_timeout: float = typer.Option(default=BASE_SETTINGS.app.ws_ping_timeout),
    reload: bool = typer.Option(default=False),
) -> None:
    service_entrypoint = SERVICES.get(service_type, None)
    if not service_entrypoint:
        raise RuntimeError(f"Service {service_type} is not supported")

    get_logger().debug(f"Starting service {service_type.value} on {host}:{port}")

    run(
        service_entrypoint,
        host=host,
        port=port,
        reload=reload,
        access_log=False,
        forwarded_allow_ips=BASE_SETTINGS.app.forwarded_allow_ips,
        factory=True,
        proxy_headers=True,
        log_level="warning",  # disable standard uvicorn loggers
        log_config=generate_uvicorn_log_config(
            log_level=BASE_SETTINGS.logging.log_level,
            log_format=BASE_SETTINGS.logging.log_format,
            is_sentry_enabled=BASE_SETTINGS.sentry.is_enabled,
            formatter=StructlogFormatter,
        ),
        ws_ping_interval=ws_ping_interval,
        ws_ping_timeout=ws_ping_timeout,
    )
