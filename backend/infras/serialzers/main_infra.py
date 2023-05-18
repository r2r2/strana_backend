from rest_framework import serializers

from .main_infra_content import MainInfraContentSerializer
from ..models import MainInfra


class MainInfraSerializer(serializers.ModelSerializer):
    maininfracontent_set = MainInfraContentSerializer(many=True, read_only=True)

    class Meta:
        model = MainInfra
        fields = "__all__"
