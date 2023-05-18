from django.db.models import TextChoices


class WorkFormat(TextChoices):
    REMOTELY = "remotely", "Удаленно"
    OFFICE = "office", "Работа из офиса"
