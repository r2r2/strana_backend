from django.contrib.sites.shortcuts import get_current_site
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_tracking.mixins import LoggingMixin

from panel_manager.tasks import process_webhook


class WebHookViewSet(LoggingMixin, APIView):
    """ВебХук для получения данных по изменению статусов встреч в AmoCRM"""
    authentication_classes = []
    permission_classes = []

    def post(self, request: Request, *args, **kwargs):
        site = get_current_site(request)
        process_webhook.delay(request.data, site.id)
        return Response(request.data)
