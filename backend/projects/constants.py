from django.db.models import TextChoices


class ProjectStatusType(TextChoices):
    CURRENT = "current", "Текущий"
    COMPLETED = "completed", "Завершенный"
    FUTURE = "future", "Будущий"


class ProjectSkyColor(TextChoices):
    DARK_BLUE = "dark_blue", "Синее"
    LIGHT_BLUE = "light_blue", "Голубое"
    AQUAMARINE = "aquamarine", "Аквамариновое"


class ProjectLabelShapeChoices(TextChoices):
    SQUARE = "square", "Квадратная"
    RECTANGLE = "rectangle", "Прямоугольная"


class ProjectAdvantageSlideChoices(TextChoices):
    LEFT = "left", "Слева"
    RIGHT = "right", "Справа"
    CENTER = "center", "Центр"
    BOTTOM = "bottom", "Снизу"


class ProjectTemplateTypeChoices(TextChoices):
    BUSINESS = "business", "Бизнес"
    COMFORT = "comfort", "Комфорт"
