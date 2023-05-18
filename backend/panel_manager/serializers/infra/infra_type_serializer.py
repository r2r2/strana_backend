import json

from rest_framework import serializers

from infras.models import InfraType
from .infra_content_serializer import InfraContentSerializer
from .infra_serializer import InfraSerializer


class InfraTypeSerializer(serializers.ModelSerializer):
    infra_set = InfraSerializer(many=True, read_only=True)

    class Meta:
        model = InfraType
        fields = "__all__"
