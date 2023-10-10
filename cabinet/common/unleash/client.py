from typing import Callable, Any
from config import maintenance_settings, unleash_config
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .cache import RCache

from .adapter import UnleashAdapter


class UnleashClient:
    client: UnleashAdapter

    def __new__(cls, logger: Any | None = structlog.getLogger(__name__)):
        if not hasattr(cls, 'instance'):
            cls.instance = super(UnleashClient, cls).__new__(cls)
            logger.info("Starting Unleash client")
            cache = RCache()
            cls.client = UnleashAdapter(
                url=unleash_config["url"],
                app_name="strana",
                instance_id=unleash_config["instance_id"],
                verbose_log_level=0,
                disable_metrics=True,
                disable_registration=True,
                # refresh_interval=60,
                cache=cache,
            )
            cls.client.initialize_client()
        return cls.instance

    def is_enabled(
        self,
        feature_name: str,
        context: dict | None = None,
        fallback_function: Callable = None,
    ) -> bool:
        feature_name = f'{feature_name.value}_{maintenance_settings["environment"].lower()}'
        is_enabled = self.client.is_enabled(
            feature_name=feature_name,
            context=context,
            fallback_function=fallback_function,
        )
        return is_enabled
