from datetime import timedelta

from rest_framework import serializers

from ..models import Statistic


class StatisticListSerializer(serializers.ModelSerializer):
    time_seconds = serializers.SerializerMethodField(label="Время в секундах")

    class Meta:
        model = Statistic
        fields = "__all__"

    def get_time_seconds(self, obj: Statistic):
        return timedelta(hours=obj.time.hour, minutes=obj.time.minute, seconds=obj.time.second)


class StatisticAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistic
        fields = ("metting", "slide", "time")
