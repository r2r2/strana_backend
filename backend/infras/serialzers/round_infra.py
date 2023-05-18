from rest_framework import serializers

from ..models import RoundInfra


class RoundInfraSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoundInfra
        fields = "__all__"
