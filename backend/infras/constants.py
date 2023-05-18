from django.db.models import TextChoices


class MainInfraType(TextChoices):
    NO = "no", "Нет"
    SMALL_PIN = "small", "Маленький пин"
    BIG_PIN = "big", "Большой пин"
