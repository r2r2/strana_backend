import hashlib

import sentry_sdk
from django.conf import settings
from django.core.cache import caches
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from graphql import Source, execute, parse
from graphql.execution.executor import subscribe
from graphql.utils.get_operation_ast import get_operation_ast
from rest_framework.views import APIView
from rx import Observable

from caches.classes import CrontabCache, ResolverCache, UserAgentCache


class SentryCachedGraphQLView(GraphQLView):
    def execute_graphql_request(
        self, request, data, query, variables, operation_name, show_graphiql=False
    ):
        chrome = "Chrome" in request.user_agent.browser.family
        cache = ResolverCache(query, variables, request.site.domain, chrome)
        if cache.cacheable:
            result = self._execute_cached_graphql_request(
                cache, chrome, request, data, query, variables, operation_name, show_graphiql
            )
        else:
            result = self._execute_default_graphql_request(
                request, data, query, variables, operation_name, show_graphiql
            )
        return result

    def _execute_cached_graphql_request(
            self, cache, chrome, request, data, query, variables, operation_name, show_graphiql=False
    ):
        cache.set_options()
        result = cache.get_result()
        if not result:
            result = super().execute_graphql_request(
                request, data, query, variables, operation_name, show_graphiql
            )
            if result and result.errors:
                self._capture_sentry_exceptions(result.errors)
            if result and not result.errors:
                cache.set_result(result)
                if cache.need_crontab:
                    CrontabCache.add(cache.name)
                if cache.need_ua:
                    UserAgentCache.set_result(request.user_agent, chrome)
        return result

    def _execute_default_graphql_request(
            self, request, data, query, variables, operation_name, show_graphiql=False
    ):
        result = super().execute_graphql_request(
            request, data, query, variables, operation_name, show_graphiql
        )
        if result and result.errors:
            self._capture_sentry_exceptions(result.errors)
        return result

    def _capture_sentry_exceptions(self, errors):
        for error in errors:
            try:
                sentry_sdk.capture_exception(error.original_error)
            except AttributeError:
                sentry_sdk.capture_exception(error)


class ExtraCachingGraphQLView(GraphQLView, APIView):
    """Класс с рядом переопределенных методов Graphene с кэшированием запросов."""
    def get_operation_ast(self, request):
        data = self.parse_body(request)
        query = request.GET.get("query") or data.get("query")

        if not query:
            return None

        source = Source(query, name="GraphQL request")

        document_ast = parse(source)
        operation_ast = get_operation_ast(document_ast, None)

        return operation_ast

    @staticmethod
    def fetch_cache_key(request):
        """ Returns a hashed cache key. """
        m = hashlib.md5()
        m.update(request.body)

        return m.hexdigest()

    def super_call(self, request, *args, **kwargs):
        response = super(ExtraCachingGraphQLView, self).dispatch(request, *args, **kwargs)

        return response

    def dispatch(self, request, *args, **kwargs):
        """ Fetches queried data from graphql and returns cached & hashed key. """
        if not settings.CACHES:
            return self.super_call(request, *args, **kwargs)

        cache = caches["default"]
        operation_ast = self.get_operation_ast(request)
        if operation_ast and operation_ast.name.value == 'allCities':
            return self.super_call(request, *args, **kwargs)
        if operation_ast and operation_ast.operation == "mutation":
            cache.clear()
            return self.super_call(request, *args, **kwargs)

        cache_key = "_graplql_{}".format(self.fetch_cache_key(request))
        response = cache.get(cache_key)

        if not response:
            response = self.super_call(request, *args, **kwargs)

            # cache key and value
            cache.set(cache_key, response, timeout=settings.CACHE_MIDDLEWARE_SECONDS)

        return response

    def execute(self, *args, **kwargs):
        operation_ast = get_operation_ast(args[0])

        if operation_ast and operation_ast.operation == "subscription":
            result = subscribe(self.schema, *args, **kwargs)
            if isinstance(result, Observable):
                a = []
                result.subscribe(lambda x: a.append(x))
                if len(a) > 0:
                    result = a[-1]
            return result

        return execute(self.schema, *args, **kwargs)

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(ExtraCachingGraphQLView, cls).as_view(*args, **kwargs)
        view = csrf_exempt(view)
        return view

    def get_response(self, request, data, show_graphiql=False):
        query, variables, operation_name, id = self.get_graphql_params(request, data)

        execution_result = self.execute_graphql_request(
            request, data, query, variables, operation_name, show_graphiql
        )

        status_code = 200
        if execution_result:
            response = {}

            if execution_result.errors:
                response["errors"] = [
                    self.format_error(e) for e in execution_result.errors
                ]

            if execution_result.invalid:
                status_code = 400
            else:
                response["data"] = execution_result.data

            if self.batch:
                response["id"] = id
                response["status"] = status_code

            result = self.response_json_encode(request, response, pretty=show_graphiql)
        else:
            result = None

        return result, status_code

    def response_json_encode(self, request, response, pretty):
        return self.json_encode(request, response, pretty)
