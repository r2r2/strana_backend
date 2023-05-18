from rest_framework import serializers

from ..models import OurProjects, ProjectsForMap, StageProjects


class OurProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurProjects
        fields = "__all__"


class StageProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StageProjects
        fields = "__all__"


class ProjectsForMapSerializer(serializers.ModelSerializer):
    stage = StageProjectsSerializer(many=False, read_only=True)

    class Meta:
        model = ProjectsForMap
        fields = "__all__"
