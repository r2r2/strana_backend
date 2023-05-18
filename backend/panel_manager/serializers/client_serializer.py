import sentry_sdk
from rest_framework import serializers

from ..models import Client


class ClientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class ClientAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("id", "name", "last_name", "patronymic", "phone", "email")


class ClientUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ("name", "last_name", "patronymic", "phone", "email")

