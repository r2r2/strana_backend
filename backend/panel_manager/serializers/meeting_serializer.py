from rest_framework import serializers

from common.rest_fields import IntegerRangeField
from .manager_serializer import ManagerSerializer
from panel_manager.serializers import ClientListSerializer, ClientUpdateSerializer
from .statistic_serializer import StatisticListSerializer
from ..models import Meeting, MeetingDetails
from drf_writable_nested import WritableNestedModelSerializer


class MeetingDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = MeetingDetails
        exclude = ('id', 'meeting',)


class MeetingListSerializer(serializers.ModelSerializer):
    client = ClientListSerializer(label="Клиент")
    # project = ProjectRetrieveSerializer(label="Проект")
    manager = ManagerSerializer(label="Менеджер")
    area = serializers.SerializerMethodField(label="Площадь")
    floor = serializers.SerializerMethodField(label="Этажность")
    details = MeetingDetailsSerializer(many=False, read_only=True)

    class Meta:
        model = Meeting
        fields = "__all__"

    def get_area(self, obj: Meeting):
        data = {}
        if obj.area:
            if obj.area.lower and obj.area.lower > 1:
                data["lower"] = obj.area.lower
            if obj.area.upper and obj.area.upper > 1:
                data["upper"] = obj.area.upper
        return data

    def get_floor(self, obj: Meeting):
        data = {}
        if obj.floor:
            if obj.floor.lower and obj.floor.lower > 1:
                data["lower"] = obj.floor.lower
            if obj.floor.upper and obj.floor.upper > 1:
                data["upper"] = obj.floor.upper
        return data


class MeetingUpdateSerializer(WritableNestedModelSerializer):
    area = IntegerRangeField()
    floor = IntegerRangeField()
    details = MeetingDetailsSerializer(many=False, read_only=False)
    client = ClientUpdateSerializer(many=False, read_only=False)

    class Meta:
        model = Meeting
        fields = "__all__"


class MeetingAddSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="client.email"
    )
    total_mortgage_amount = serializers.IntegerField(
        source="details.total_mortgage_amount"
    )

    class Meta:
        model = Meeting
        fields = ("id", "client", "manager", "email", "total_mortgage_amount")


class MeetingStatisticSerializer(serializers.ModelSerializer):
    manager = ManagerSerializer(label="Менеджер")
    # project = ProjectRetrieveSerializer(label="Проект")
    all_time = serializers.SerializerMethodField(label="Общее время")
    slides = StatisticListSerializer(source="statistic_set", many=True)

    id = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = ("id", "manager", "project", "client", "all_time", "slides")

    def get_all_time(self, obj: Meeting):
        if obj.all_time:
            return obj.all_time.seconds
        return None

    def get_id(self, obj:Meeting):
        """Замена id на id_crm"""
        return str(getattr(obj, 'id_crm', obj.id))
