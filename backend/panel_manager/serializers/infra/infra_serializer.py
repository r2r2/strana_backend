import json

from rest_framework import serializers

from infras.models import Infra
from .infra_content_serializer import InfraContentSerializer


class InfraSerializer(serializers.ModelSerializer):
    infracontent_set = InfraContentSerializer(many=True, read_only=True)

    class Meta:
        model = Infra
        fields = "__all__"
