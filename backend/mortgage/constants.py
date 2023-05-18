from django.db.models import TextChoices


class MortgageType(TextChoices):
    COMMERCIAL = "commercial", "Коммерческая ипотека"
    RESIDENTIAL = "residential", "Жилая ипотека"


class DvizhProgramType(TextChoices):
    STANDARD = "STANDARD", "Стандартная ипотека"
    FAMILY = "FAMILY", "Семейная ипотека"
    MILITARY = "MILITARY", "Военная ипотека"
    GOVERNMENT_SUPPORT = "GOVERNMENT_SUPPORT", "Государственная поддержка 2020 (пандемия COVID-19)"
