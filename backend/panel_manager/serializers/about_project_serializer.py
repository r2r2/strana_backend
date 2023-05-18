from rest_framework.serializers import ModelSerializer

from common.rest_fields import MultiImageField
from panel_manager.models import (
    PinsAboutProjectGallery,
    AboutProjectGallery,
    AboutProjectGalleryCategory,
    AboutProject,
    AboutProjectParametrs,
)


class PinsAboutProjectGallerySeriazlier(ModelSerializer):
    class Meta:
        model = PinsAboutProjectGallery
        fields = "__all__"


class AboutProjectGallerySeriazlier(ModelSerializer):
    image_display = MultiImageField()
    image_preview = MultiImageField()
    pinsaboutprojectgallery_set = PinsAboutProjectGallerySeriazlier(many=True, read_only=True)

    class Meta:
        model = AboutProjectGallery
        fields = "__all__"


class AboutProjectGalleryCategorySeriazlier(ModelSerializer):
    icon_display = MultiImageField()
    icon_preview = MultiImageField()
    aboutprojectgallery_set = AboutProjectGallerySeriazlier(many=True, read_only=True)

    class Meta:
        model = AboutProjectGalleryCategory
        fields = "__all__"


class AboutProjectParametrsSeriazlier(ModelSerializer):
    class Meta:
        model = AboutProjectParametrs
        fields = "__all__"


class AboutProjectSeriazlier(ModelSerializer):
    parametrs = AboutProjectParametrsSeriazlier(
        many=True, read_only=True, source="aboutprojectparametrs_set"
    )

    class Meta:
        model = AboutProject
        fields = "__all__"


class AboutProjectGalleryForSlidesSeriazlier(ModelSerializer):
    image_display = MultiImageField()
    image_preview = MultiImageField()
    category = AboutProjectGalleryCategorySeriazlier(read_only=True, many=False)

    class Meta:
        model = AboutProjectGallery
        fields = "__all__"
