from rest_framework import serializers

from users.serializers import UserSerializer

from ..models import Manager, Role


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = "__all__"


class ManagerSerializer(serializers.ModelSerializer):
    user = UserSerializer(label="Пользователь")
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = Manager
        fields = "__all__"


class ManagerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(label="Email/Login")
    password = serializers.CharField(label="Password")

    def validate(self, attrs):
        manager = Manager.objects.filter(login=attrs["username"]).first()
        if manager:
            attrs["user"] = manager.user
            attrs["manager"] = manager
        return super().validate(attrs)
