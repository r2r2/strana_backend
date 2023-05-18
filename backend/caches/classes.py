from __future__ import annotations
from json import dumps, loads
from sentry_sdk import capture_exception
from typing import Any, Dict, List
from base64 import b64encode, b64decode
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.http import HttpRequest
from graphene_django.views import GraphQLView
from rest_framework.request import Request
from user_agents.parsers import UserAgent
from app.settings import TESTING
from favorite.classes import Favorite
from django.utils.decorators import classproperty
from django.contrib.sessions.backends.cache import SessionStore
from .storages import query_storage
from .exceptions import CacheError


class ResolverCache(object):
    """
    Кэш для определенных резолверов
    """

    _crontab_cache_name = "cache_update_list"
    _storage = query_storage
    _cache = cache
    _skip = "SKIP"

    def __init__(self, query, variables, domain, chrome) -> None:
        self._query = query
        self._variables = variables
        self._domain = domain
        self._chrome = dumps(chrome)

        self._result = None
        self._name = None
        self._cacheable = None
        self._gql_data = None
        self._operation = None

        self._use_variables = False
        self._use_domain = False
        self._use_user_agent = False
        self._use_crontab = False
        self._cache_time = 3600

    @classmethod
    def init_from_cache(cls, name) -> ResolverCache:
        """
        Инициалиция из кэша по имени
        """
        components = name.split("_")
        query = b64decode(components[0]).decode("utf-8")
        domain = components[1] if components[1] != cls._skip else None
        chrome = loads(components[2]) if components[1] != cls._skip else False
        variables = b64decode(components[3]).decode("utf-8") if components[3] != cls._skip else None
        crontab = loads(components[4])
        time = int(components[5])
        self = cls(query, variables, domain, chrome)
        self._name = name
        self._cacheable = True
        self._use_domain = bool(domain)
        self._use_user_agent = bool(chrome)
        self._use_variables = bool(variables)
        self._use_crontab = bool(crontab)
        self._cache_time = time
        self._gql_data = {"query": query, "variables": variables, "operationName": None}
        return self

    @property
    def cacheable(self) -> bool:
        """
        Проверка на необходимость кэширования запроса
        """
        if self._cacheable is None:
            self._cacheable = True
            if not self._query:
                self._cacheable = False
            if self.operation not in self._storage.queries:
                self._cacheable = False
            if TESTING:
                self._cacheable = False
        return self._cacheable

    @property
    def operation(self) -> str:
        """
        Получение имени операции
        """
        if not self._operation:
            try:
                operation = "".join(
                    self._query[self._query.find("{") + 1 :][
                        : self._query[self._query.find("{") + 1 :].find("{")
                    ].split()
                )
                if operation.count("("):
                    operation = operation[: operation.find("(")]
            except (IndexError, AttributeError):
                operation = None
            self._operation = operation
        return self._operation

    @property
    def name(self) -> str:
        """
        Получение имени кэша
        """
        if self._cacheable is None:
            raise CacheError("Cacheable check was not provided.")
        if not self._cacheable:
            raise CacheError("Cannot access name in case of uncacheability")
        if self._name is None:
            name = b64encode(self._query.encode("utf-8")).decode("utf-8")
            if self._domain and self._use_domain:
                name += "_" + self._domain
            else:
                name += "_" + self._skip
            if self._use_user_agent:
                name += "_" + self._chrome
            else:
                name += "_" + self._skip
            if self._variables and self._use_variables:
                name += "_" + b64encode(dumps(self._variables).encode("utf-8")).decode("utf-8")
            else:
                name += "_" + self._skip
            name += "_" + dumps(self._use_crontab) + "_" + str(self._cache_time)
            self._name = name
        return self._name

    @property
    def need_crontab(self) -> bool:
        """
        Нужно ли добавлять в кронтаб
        """
        return self._use_crontab

    @property
    def need_ua(self) -> bool:
        """
        Нужен ли ЮА
        """
        return self._use_user_agent

    def set_result(self, result) -> None:
        """
        Установка резульата в кэш
        """
        self._cache.set(self.name, result, self._cache_time)

    def set_options(self) -> None:
        """
        Установка опций из декоратора
        """
        options = self._storage[self._operation]
        self._use_variables = options.get("variables", False)
        self._use_domain = options.get("domain", False)
        self._use_user_agent = options.get("user_agent", False)
        self._cache_time = options.get("time", 3600)
        self._use_crontab = options.get("crontab", False)

    def get_result(self) -> Any:
        """
        Получение результата из кэша
        """
        if self._result is None:
            self._result = self._cache.get(self.name)
        return self._result

    @property
    def updatable(self) -> bool:
        """
        Может ли кэш быть обновлен
        """
        return bool(self._query and self._domain and self._chrome and self._name)

    @property
    def site(self) -> Site:
        """
        Сайт кэша
        """
        if self._domain and self._use_domain:
            return Site.objects.filter(domain=self._domain).first()
        return Site.objects.first()

    @property
    def update_data(self) -> Dict[str, Any]:
        """
        Данные для обновления кэша
        """
        data = dict(
            request=self.request,
            data=self._gql_data,
            query=self._query,
            variables=self._variables,
            operation_name=None,
        )
        return data

    @property
    def request(self) -> Request:
        """
        Запрос для эмуляции
        """
        django_request = HttpRequest()
        django_request.META = {"HTTP_X_FORWARDED_HOST": self.site.domain}
        rest_request = Request(django_request)
        rest_request.site = self.site
        rest_request.method = "POST"
        rest_request.user_agent = UserAgentCache.get_result(loads(self._chrome))
        rest_request.session = SessionStore()
        rest_request.favorite = Favorite(rest_request.session)
        return rest_request


class UserAgentCache(object):
    """
    Кэш юзер агентов
    """

    _cache = cache
    _cache_time = 3600
    _name = "user_agent_browsers"
    _webp_name = "webp"
    _default_name = "default"
    _default = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
    )

    @classmethod
    def set_result(cls, user_agent, chrome) -> None:
        browsers = cls._cache.get(cls._name)
        name = cls._webp_name if chrome else cls._default_name
        if not browsers:
            browsers = {name: user_agent.ua_string}
        else:
            browsers[name] = user_agent.ua_string
        cls._cache.set(cls._name, browsers, cls._cache_time)

    @classmethod
    def get_result(cls, chrome) -> UserAgent:
        browsers = cls._cache.get(cls._name)
        name = cls._webp_name if chrome else cls._default_name
        if not browsers:
            return UserAgent(cls._default)
        ua_string = browsers.get(name, str())
        if not ua_string:
            return UserAgent(cls._default)
        return UserAgent(ua_string)


class CrontabCache(object):
    """
    Обновление кэшей в кронтабе
    Необходим отдельный контейнер, воркер, очередь
    """

    _view = GraphQLView()
    _name = "cache_update_list"
    _cache = cache
    _cache_time = 3600
    _chunk_size = 10
    _time_multiplicator = 1.5
    _update_time = 20
    _caches = []

    @classproperty
    def chunks(cls) -> List[List[str]]:
        """
        Разделение кэшей на равные части
        """
        chunks = list()
        caches = cls.caches
        if caches:
            for i in range(0, len(caches), cls._chunk_size):
                chunks.append(caches[i : i + cls._chunk_size])
        return chunks

    @classproperty
    def caches(cls) -> List[str]:
        """
        Получение списка имен кэшей для обновления
        """
        return cls._cache.get(cls._name)

    @classmethod
    def update_chunk(cls, chunk) -> None:
        """
        Обновление части кэшей
        """
        for name in chunk:
            try:
                resolver_cache = ResolverCache.init_from_cache(name)
                if resolver_cache.updatable:
                    result = cls.result(**resolver_cache.update_data)
                    resolver_cache.set_result(result)
            except Exception as error:
                capture_exception(error)

    @classmethod
    def result(cls, **kwargs) -> Any:
        """
        Выполнение запроса
        """
        return cls._view.execute_graphql_request(**kwargs)

    @classmethod
    def clear(cls) -> None:
        """
        Очистка кэша
        """
        cls._cache.set(cls._name, list(), cls._cache_time)

    @classmethod
    def refresh(cls) -> None:
        """
        Обновление кронтаб кэша
        """
        cls._cache.set(cls._name, cls.caches, cls._cache_time)

    @classmethod
    def add(cls, name) -> None:
        """
        Добавляет кэш в кронтаб
        """
        caches = cls.caches
        if not caches:
            cls._cache.set(cls._name, [name], cls._cache_time)
        else:
            caches.append(name)
            cls._cache.set(cls._name, caches, cls._cache_time)
