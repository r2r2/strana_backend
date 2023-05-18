import json
import re
import threading
import time
from queue import Queue

from django.conf import settings
from django.http import HttpResponse
from django.urls import resolve
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from rest_framework_tracking.models import APIRequestLog


class NonHtmlDebugToolbarMiddleware(MiddlewareMixin):
    """
    The Django Debug Toolbar usually only works for views that return HTML.
    This middleware wraps any non-HTML response in HTML if the request
    has a 'debug' query parameter (e.g. http://localhost/foo?debug)
    Special handling for json (pretty printing) and
    binary data (only show data length)
    """

    @staticmethod
    def process_response(request, response):
        debug = request.GET.get('debug', 'UNSET')

        if debug != 'UNSET':
            if response['Content-Type'] == 'application/octet-stream':
                new_content = '<html><body>Binary Data, ' 'Length: {}</body></html>'.format(
                    len(response.content)
                )
                response = HttpResponse(new_content)
            elif response['Content-Type'] != 'text/html':
                content = response.content
                try:
                    json_ = json.loads(content)
                    content = json.dumps(json_, sort_keys=True, indent=2)
                except ValueError:
                    pass
                response = HttpResponse(
                    '<html><body><pre>{}' '</pre></body></html>'.format(content)
                )

        return response


class BatchCreateLogRecords(threading.Thread):
    """Выделенный поток для хранения n запросов в памяти перед записью в БД."""
    def __init__(self):
        super(BatchCreateLogRecords, self).__init__()
        self.MAX_RECORDS = settings.API_LOGGING_SETTINGS["BATCH_SIZE"]
        self._queue = []

    def run(self) -> None:
        self.start_process()

    def put_log_data(self, data: dict):
        """Добавление объекта записи в очередь."""
        self._queue.append(APIRequestLog(**data))

    def start_process(self):
        while True:
            time.sleep(10)
            if len(self._queue) >= self.MAX_RECORDS:
                self._start_bulk_create()

    def _start_bulk_create(self):
        if not self._queue:
            return
        APIRequestLog.objects.bulk_create(self._queue)
        self._queue = []


if settings.API_LOGGING_SETTINGS["LOGGING_ENABLED"]:
    LOG_THREAD_NAME = "batch_create_log"
    thread_exists = False
    for t in threading.enumerate():
        if t.name == LOG_THREAD_NAME:
            thread_exists = True
            break
    if not thread_exists:
        thread = BatchCreateLogRecords()
        thread.daemon = True
        thread.name = LOG_THREAD_NAME
        thread.start()
        LOGGER_THREAD = thread


class APIRequestMiddleware(MiddlewareMixin):
    """Журналирование всех входящих запросов.

    NB! При включенном Django-Debug-Toolbar происходит дублирование вызовов middleware.
    Соответственно, в журналах записи так же могут дублироваться.
    """

    @staticmethod
    def get_headers(request=None):
        """
            Function:       get_headers(self, request)
            Description:    To get all the headers from request
        """
        regex = re.compile('^HTTP_')
        return dict((regex.sub('', header), value) for (header, value)
                    in request.META.items() if header.startswith('HTTP_'))

    @staticmethod
    def get_client_ip(request):
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip
        except:
            return ''

    def process_request(self, request):
        if not settings.API_LOGGING_SETTINGS["LOGGING_ENABLED"]:
            return self.get_response(request)
        url_name = resolve(request.path_info).url_name
        namespace = resolve(request.path_info).namespace
        if (namespace in settings.API_LOGGING_SETTINGS["SKIP_URL_NAMESPACES"]
                or url_name in settings.API_LOGGING_SETTINGS["SKIP_URL_NAMES"]):
            return self.get_response(request)
        start_time = timezone.now()
        response = self.get_response(request)
        dt_response = (timezone.now() - start_time).microseconds // 10
        headers = self.get_headers(request)
        try:
            request_data = request.body.decode()
        except:
            request_data = ""
        if request_data and request.content_type == "application/json":
            try:
                request_data = json.loads(request.body.decode())
            except json.JSONDecodeError:
                pass
        try:
            response_data = response.content.decode()
        except:
            response_data = ""
        if response_data and request.content_type == "application/json":
            try:
                response_data = json.loads(response_data)
            except json.JSONDecodeError:
                pass
        data = dict(
            user=request.user if request.user.is_authenticated else None,
            requested_at=timezone.now(),
            path=request.path,
            data=str(request_data).replace("\n", "").replace("\r", ""),
            remote_addr=self.get_client_ip(request),
            host=request.get_host(),
            status_code=response.status_code,
            method=request.method,
            response_ms=dt_response,
            response=response_data,
            query_params=str(request.GET) if request.GET else None
        )
        if LOGGER_THREAD:
            LOGGER_THREAD.put_log_data(data)
        return response
