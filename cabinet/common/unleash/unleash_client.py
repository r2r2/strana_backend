from typing import Callable, Any
from UnleashClient import UnleashClient
from config import maintenance_settings, unleash_config
import structlog


class UnleashAdapter:
    client: UnleashClient

    def __new__(cls, logger: Any | None = structlog.getLogger(__name__)):
        if not hasattr(cls, 'instance'):
            cls.instance = super(UnleashAdapter, cls).__new__(cls)
            logger.info("Starting Unleash client")
            cls.client = UnleashClient(
                url=unleash_config["url"],
                app_name="strana",
                instance_id=unleash_config["instance_id"],
                verbose_log_level=0,
                disable_metrics=True,
                disable_registration=True,
                refresh_interval=60,
                cache_directory="./feature_flag"
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
        print(feature_name)
        is_enabled = self.client.is_enabled(
            feature_name=feature_name,
            context=context,
            fallback_function=fallback_function,
        )
        print("Feature flag name: ", feature_name)
        print("Feature flag enabled: ", is_enabled)
        return is_enabled
