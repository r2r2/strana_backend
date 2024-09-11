import tomllib
from functools import lru_cache
from typing import Type, cast

from boilerplates.logging import LogFormat
from boilerplates.sentry import SentrySettings
from dynaconf import Dynaconf
from pydantic import BaseModel, ConfigDict, SecretStr

from src.constants import SETTINGS_PATH
from src.core.types import PydanticModel


class DynaconfSettings(BaseModel):
    """Dynaconf-compatible settings"""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda name: name.upper(),
    )


class LoggingSettings(DynaconfSettings):
    log_format: LogFormat
    log_level: str
    spammy_loggers: list[str]


class CORSSettings(DynaconfSettings):
    is_enabled: bool
    allow_origins: list[str]
    allow_credentials: bool
    allow_methods: list[str]
    allow_headers: list[str]


class SwaggerDocsSettings(DynaconfSettings):
    is_enabled: bool
    username: str
    password: SecretStr


class AppSettings(DynaconfSettings):
    title: str
    host: str
    port: int
    debug: bool
    api_root_path: str
    forwarded_allow_ips: str
    ws_ping_interval: float | None = 20.0  # default values from uvicorn server
    ws_ping_timeout: float | None = 60.0

    @property
    def version(self) -> str:
        return get_app_version()


class BaseServiceSettings(DynaconfSettings):
    app: AppSettings
    logging: LoggingSettings
    sentry: SentrySettings
    cors: CORSSettings
    docs: SwaggerDocsSettings


@lru_cache(typed=True)
def get_app_version() -> str:
    try:
        with open("pyproject.toml", "rb") as pyproject_f:
            proj_config = tomllib.load(pyproject_f)
            return cast(str, proj_config["tool"]["poetry"]["version"])

    except tomllib.TOMLDecodeError as exc:
        raise RuntimeError("Invalid TOML structure in pyproject.toml") from exc

    except FileNotFoundError as exc:
        raise RuntimeError("pyproject.toml was not found in the workdir") from exc


def load_settings(model: Type[PydanticModel], section_name: str | None = None) -> PydanticModel:
    _settings_dict = Dynaconf(
        core_loaders=["YAML"],
        default_env="default",
        environments=["default", "test"],
        env_switcher="MESSENGER_ENV",
        envvar_prefix="MESSENGER_POSTBACK",
        load_dotenv=False,
        settings_files=[SETTINGS_PATH],
        yaml_loader="safe_load",
    )
    target = dict(_settings_dict)
    if section_name and not (target := target.get(section_name.upper(), None)):
        raise ValueError(f"Settings section not found: {section_name}")

    return model(**target)


BASE_SETTINGS = load_settings(BaseServiceSettings)


__all__ = (
    "BASE_SETTINGS",
    "load_settings",
    "BaseServiceSettings",
    "AppSettings",
    "LoggingSettings",
    "CORSSettings",
    "SentrySettings",
    "SwaggerDocsSettings",
)
