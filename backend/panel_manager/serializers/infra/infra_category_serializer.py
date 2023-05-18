from rest_framework import serializers

from infras.models import InfraCategory
from panel_manager.serializers.infra.infra_type_serializer import InfraTypeSerializer


class InfraCategorySerializer(serializers.ModelSerializer):
    icon = serializers.FileField()
    infratype_set = InfraTypeSerializer(many=True, read_only=True)

    class Meta:
        model = InfraCategory
        fields = "__all__"
