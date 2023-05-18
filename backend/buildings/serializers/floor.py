from rest_framework import serializers

from ..models import Floor


class FloorSerializer(serializers.ModelSerializer):
    plan = serializers.FileField(required=False, read_only=True)

    class Meta:
        model = Floor
        exclude = ("section",)
