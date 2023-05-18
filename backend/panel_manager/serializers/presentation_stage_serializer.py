from rest_framework.serializers import ModelSerializer, SerializerMethodField

from . import AboutProjectGalleryCategorySeriazlier
from ..models import PresentationStage


class PresentationStageListSerializer(ModelSerializer):

    about_project_slides = AboutProjectGalleryCategorySeriazlier(many=True, read_only=True)
    hard_type_name = SerializerMethodField(label="Наименование")

    class Meta:
        model = PresentationStage
        fields = "__all__"

    def get_hard_type_name(self, obj: PresentationStage):
        return obj.get_hard_type_display()
