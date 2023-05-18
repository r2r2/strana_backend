from rest_framework import serializers

from ..models import SubInfra


class SubInfraSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubInfra
        fields = "__all__"
