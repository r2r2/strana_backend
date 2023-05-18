from django.db.models import TextChoices


class WorkFormat(TextChoices):
    REMOTELY = "remotely", "Удаленно"
    OFFICE = "office", "Работа из офиса"


class BlockType(TextChoices):
    BANK = "bank", "Банк"
    AGENT = "agent", "Агент"
    CONTRACTOR = "contractor", "Подрядчик"
    SALE_PLOT = "sale_plot", "Продажа земельного участка"
    MEDIA = "media", "Блок для СМИ"


class PersonCategory(TextChoices):
    DIRECTOR = "director", "Директор"
    MANAGER = "manager", "Менеджер"
