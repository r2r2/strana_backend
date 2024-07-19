from jobs.constants import SETTINGS_PATH
from jobs.internal.app_settings import Settings
from sdk.settings import load_config


def get_config() -> Settings:
    settings: Settings = load_config(SETTINGS_PATH, settings_class=Settings)  # type: ignore
    return settings  # noqa: PIE781
