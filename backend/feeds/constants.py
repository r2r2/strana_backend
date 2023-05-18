from django.db.models import TextChoices


class FeedType(TextChoices):
    YANDEX = "yandex", "Яндекс"
    CIAN = "cian", "Циан"
    AVITO = "avito", "Авито"
