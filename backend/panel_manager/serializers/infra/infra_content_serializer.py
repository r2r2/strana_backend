from rest_framework import serializers

from infras.models import InfraContent


class InfraContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfraContent
        fields = "__all__"
