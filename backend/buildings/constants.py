from django.db import models


class BuildingType(models.TextChoices):
    RESIDENTIAL = "RESIDENTIAL", "Жилое"
    APARTMENT = "APARTMENT", "Апартаменты"
    PARKING = "PARKING", "Паркинг"
    OFFICE = "OFFICE", "Коммерческое"
