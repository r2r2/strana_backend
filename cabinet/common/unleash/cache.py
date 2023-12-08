from typing import Any
from redis import Redis
from datetime import timedelta
from config import redis_config
import requests
from UnleashClient.cache import BaseCache
import pickle
from .decorator import return_on_failure


class RCache(BaseCache):
    FEATURES_URL = "features"
    REQUEST_TIMEOUT = 30

    def __init__(self):
        self.client = Redis(
            host=redis_config['host'],
            port=redis_config['port'],
            db=redis_config['db'],
        )

    def bootstrap_from_url(
        self, initial_config_url: str, headers: dict | None = None
    ) -> None:
        """
        Loads initial Unleash configuration from a url.

        Note: Pre-seeded configuration will only be used if UnleashClient is initialized with `bootstrap=true`.

        :param initial_configuration_url: Url that returns document containing initial configuration.  Must return JSON.
        :param headers: Headers to use when GETing the initial configuration URL.
        """
        response = requests.get(
            initial_config_url, headers=headers, timeout=self.REQUEST_TIMEOUT
        )
        self.set(self.FEATURES_URL, response.json())
        self.bootstrapped = True

    @return_on_failure(None)
    def get(self, key: str, default: Any | None = None):
        return pickle.loads(self.client.get(name=key))

    @return_on_failure(None)
    def set(self, key: str, value: Any, expire: int | None = None):
        ex = None
        if expire:
            ex = timedelta(seconds=expire)
        self.client.set(name=key, value=pickle.dumps(value), ex=ex)

    @return_on_failure(None)
    def mset(self, data: dict):
        data['mlst'] = data['mlst'].strftime("%m/%d/%Y, %H:%M:%S")
        self.client.mset(mapping=data)

    @return_on_failure(None)
    def exists(self, key: str):
        return self.client.exists()

    def destroy(self):
        pass
