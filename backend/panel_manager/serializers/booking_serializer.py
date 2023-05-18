from rest_framework import serializers


class BookingSerializer(serializers.Serializer):
    meeting = serializers.UUIDField(label="Встреча")
