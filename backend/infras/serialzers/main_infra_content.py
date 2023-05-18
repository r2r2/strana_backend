from rest_framework import serializers

from ..models import MainInfraContent


class MainInfraContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainInfraContent
        fields = "__all__"
