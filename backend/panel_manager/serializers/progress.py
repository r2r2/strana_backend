from pprint import pprint
from typing import Union

from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.serializers import ModelSerializer

from common.rest_fields import MultiImageField
from news.models import News, NewsSlide
from ..models import Progress
from .progress_gallery import ProgressGalleryRetrieveSerializer
from .progress_category import ProgressCategoryListSerializer


class ProgressListSerializer(ModelSerializer):
    """
    Сериализатор списка ходов строительства
    """

    month = SerializerMethodField(required=False, read_only=True)

    photo_count = IntegerField(required=False, read_only=True)
    video_count = IntegerField(required=False, read_only=True)

    image_display = MultiImageField(required=False, read_only=True)
    image_preview = MultiImageField(required=False, read_only=True)

    @staticmethod
    def get_month(obj: Progress) -> Union[str, None]:
        month: Union[str, None] = obj.get_month_display()
        return month

    class Meta:
        model = Progress
        fields = (
            "id",
            "year",
            "month",
            "quarter",
            "photo_count",
            "video_count",
            "image_display",
            "image_preview",
        )


class ProgressRetrieveSerializer(ModelSerializer):
    """
    Сериализатор детального хода строительства
    """

    progressgallery_set = ProgressGalleryRetrieveSerializer(
        required=False, read_only=True, many=True
    )

    progresscategory_set = ProgressCategoryListSerializer(required=False, read_only=True, many=True)

    image_display = MultiImageField(required=False, read_only=True)
    image_preview = MultiImageField(required=False, read_only=True)

    class Meta:
        model = Progress
        fields = "__all__"


class _NewsSlideSerializer(ModelSerializer):
    image_display = MultiImageField(required=False, read_only=True)
    image_preview = MultiImageField(required=False, read_only=True)
    image_card_display = MultiImageField(required=False, read_only=True)
    image_card_preview = MultiImageField(required=False, read_only=True)
    preview_display = MultiImageField(required=False, read_only=True)
    preview_preview = MultiImageField(required=False, read_only=True)
    building_name_display = SerializerMethodField(label="Наименование корпуса")

    class Meta:
        model = NewsSlide
        fields = [
            "id",
            "image_display",
            "image_preview",
            "image_card_display",
            "image_card_preview",
            "preview_display",
            "preview_preview",
            "building_name_display",
            "title",
            "description",
            "video_url",
            "video_length",
            "image",
            "preview",
            "video",
        ]
        read_only_fields = fields

    def get_building_name_display(self, obj: NewsSlide):
        if obj.building:
            return str(obj.building)
        return ""


class ProgressNewsRetrieveSerializer(ModelSerializer):
    """
    Сериализатор списка ходов строительства на основе новстей
    """

    card_image_display = MultiImageField(required=False, read_only=True)
    card_image_preview = MultiImageField(required=False, read_only=True)
    image_display = MultiImageField(required=False, read_only=True)
    image_preview = MultiImageField(required=False, read_only=True)

    newsslide_set = _NewsSlideSerializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = "__all__"


class ProgressNewsListSerializer(ModelSerializer):
    """
    Сериализатор списка ходов строительства на основе новстей
    """

    year = SerializerMethodField()
    month = SerializerMethodField()
    month_display = SerializerMethodField()
    month_number = SerializerMethodField()
    quarter = SerializerMethodField()

    card_image_display = MultiImageField(required=False, read_only=True)
    card_image_preview = MultiImageField(required=False, read_only=True)
    image_display = MultiImageField(required=False, read_only=True)
    image_preview = MultiImageField(required=False, read_only=True)

    newsslide_set = _NewsSlideSerializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = [
            "id",
            "year",
            "month",
            "month_display",
            "month_number",
            "quarter",
            "card_image_display",
            "card_image_preview",
            "image_display",
            "image_preview",
            "newsslide_set",
            "title",
            "link",
            "slug",
            "type",
            "intro",
            "short_description",
            "text",
            "published",
            "is_display_flat_listing",
            "colored_title",
            "video_url",
            "video_length",
            "start",
            "end",
            "date",
            "card_image",
            "card_description",
            "image",
            "source_link",
            "button_name",
            "button_link",
            "button_blank",
            "order",
            "mass_media",
        ]
        read_only_fields = fields

    @staticmethod
    def get_year(obj: News) -> Union[str, None]:
        return getattr(obj, "year", None)

    @staticmethod
    def get_month(obj: News) -> Union[str, None]:
        return getattr(obj, "month", None)

    @staticmethod
    def get_month_display(obj: News) -> Union[str, None]:
        return getattr(obj, "month_display", None)

    @staticmethod
    def get_month_number(obj: News) -> Union[str, None]:
        return getattr(obj, "month_number", None)

    @staticmethod
    def get_quarter(obj: News) -> Union[str, None]:
        return getattr(obj, "quarter", None)
