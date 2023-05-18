from ckeditor.fields import RichTextField
from colorful.fields import RGBColorField
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import models
from common.fields import PpoiField
from .constants import MainInfraType


class InfraCategory(models.Model):
    """
    Категория инфраструктуры на карте
    """

    name = models.CharField(verbose_name="Название типа", max_length=100)
    color = RGBColorField(verbose_name="Цвет", default="#FFFFFF")
    icon = models.FileField(
        verbose_name="Иконка для списка", upload_to="infratype/icon", blank=True, null=True
    )
    icon_content = models.TextField(verbose_name="Контент иконки", null=True, blank=True)
    order = models.PositiveIntegerField(verbose_name="Порядок", default=0, db_index=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if self.icon:
            with default_storage.open(self.icon.name) as icon_file:
                icon_content = icon_file.read()
                if isinstance(icon_content, bytes):
                    icon_content = icon_content.decode("utf-8")
                icon_content.replace("\n", "").replace("b'", "")
                if icon_content.endswith("'"):
                    icon_content = icon_content[:-1]
            InfraCategory.objects.filter(id=self.id).update(icon_content=icon_content)
            self.refresh_from_db()

    class Meta:
        verbose_name = "Категория инфраструктуры на карте"
        verbose_name_plural = "Категории инфраструктуры на карте"
        ordering = ("order",)


class InfraType(models.Model):
    """
    Тип инфраструктуры на карте
    """

    name = models.CharField(verbose_name="Название", max_length=100)

    category = models.ForeignKey(
        verbose_name="Категория", to=InfraCategory, on_delete=models.CASCADE
    )

    order = models.PositiveIntegerField(verbose_name="Порядок", default=0, db_index=True)

    def __str__(self) -> str:
        return f"{self.category} - {self.name}"

    class Meta:
        verbose_name = "Тип инфраструктуры на карте"
        verbose_name_plural = "Типы инфраструктуры на карте"
        ordering = ("order",)


class Infra(models.Model):
    """
    Инфрастрктура на карте
    """

    show_in_site = models.BooleanField("Активная инфраструктура", default=True)
    show_in_panel = models.BooleanField("Показывать на панели менеджера", default=False)

    name = models.CharField(verbose_name="Название", max_length=100)
    address = models.CharField(verbose_name="Адрес", max_length=200, blank=True)
    description = RichTextField(verbose_name="Описание", blank=True)
    exploitation = models.DateField(verbose_name="Срок сдачи", null=True, blank=True)
    is_main = models.BooleanField(verbose_name="Главная", default=False)
    main_type = models.CharField(
        verbose_name="Категория основное",
        max_length=24,
        default=MainInfraType.NO,
        choices=MainInfraType.choices,
    )

    latitude = models.DecimalField(
        verbose_name="Широта", decimal_places=6, max_digits=9, null=True, blank=True
    )
    longitude = models.DecimalField(
        verbose_name="Долгота", decimal_places=6, max_digits=9, null=True, blank=True
    )

    project = models.ForeignKey(
        verbose_name="Проект", to="projects.Project", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        verbose_name="Категория", to=InfraCategory, on_delete=models.CASCADE
    )
    type = models.ForeignKey(
        verbose_name="Тип", to=InfraType, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.name} - {self.address}"

    def clean(self) -> None:
        if self.type:
            if self.type.category != self.category:
                raise ValidationError(
                    {"type": "Тип должен соответсвовать категории '%s'" % self.category}
                )

    class Meta:
        verbose_name = "Инфраструктура на карте"
        verbose_name_plural = "Инфраструктуры на карте"


class InfraContent(models.Model):
    """
    Контент инфраструктуры на карте
    """

    name = models.CharField(verbose_name="Имя", max_length=50)
    value = models.CharField(verbose_name="Значение", max_length=50)

    infra = models.ForeignKey(verbose_name="Инфраструктура", to=Infra, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Контент инфраструктуры на карте"
        verbose_name_plural = "Контенты инфраструктуры на карте"


class MainInfra(models.Model):
    """
    Главная инфраструктура на генплане
    """

    name = models.CharField(verbose_name="Название", max_length=100)
    type = models.CharField(verbose_name="Тип", max_length=50, null=True, blank=True)
    add_text = models.CharField(verbose_name="Доп текст", max_length=200, null=True, blank=True)
    address = models.CharField(verbose_name="Адрес", max_length=200, blank=True)
    is_open_left = models.BooleanField(verbose_name="Открывать инфраструктуру слева", default=False)
    color = RGBColorField(verbose_name="Цвет", default="#FFFFFF")
    icon = models.FileField(
        verbose_name="Иконка для списка", blank=True, null=True, upload_to="maininfra/icon"
    )
    icon_content = models.TextField(verbose_name="Контент иконки", null=True, blank=True)
    exploitation = models.DateField(verbose_name="Срок сдачи", null=True, blank=True)
    point = PpoiField(
        verbose_name="Точка на генплане", source="project.plan", null=True, blank=True
    )

    project = models.ForeignKey(
        verbose_name="Проект", to="projects.Project", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.name} - {self.project.name}"

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if self.icon:
            with default_storage.open(self.icon.name) as icon_file:
                icon_content = icon_file.read()
                if isinstance(icon_content, bytes):
                    icon_content = icon_content.decode("utf-8")
                icon_content.replace("\n", "").replace("b'", "")
                if icon_content.endswith("'"):
                    icon_content = icon_content[:-1]
            MainInfra.objects.filter(id=self.id).update(icon_content=icon_content)
            self.refresh_from_db()

    class Meta:
        verbose_name = "Главная инфраструктура на генплане"
        verbose_name_plural = "Главные инфраструктуры на генплане"


class MainInfraContent(models.Model):
    """
    Контент главной инфраструктуры
    """

    name = models.CharField(verbose_name="Имя", max_length=50)
    value = models.CharField(verbose_name="Значение", max_length=50)

    main_infra = models.ForeignKey(
        verbose_name="Главная инфраструктура", to=MainInfra, on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Контент главной инфраструктуры"
        verbose_name_plural = "Контенты главной инфраструктуры"


class SubInfra(models.Model):
    """
    Дополнительная инфраструктура на генплане
    """

    name = models.CharField(verbose_name="Название", max_length=100)
    type = models.CharField(verbose_name="Тип", max_length=50, null=True, blank=True)
    add_text = models.CharField(verbose_name="Доп текст", max_length=200, null=True, blank=True)
    color = RGBColorField(verbose_name="Цвет", default="#FFFFFF")
    link = models.CharField(verbose_name="Ссылка инфраструктуры", blank=True, max_length=300)
    is_open_left = models.BooleanField(verbose_name="Открывать инфраструктуру слева", default=False)

    icon = models.FileField(
        verbose_name="Иконка для списка", blank=True, null=True, upload_to="subinfra/icon"
    )
    icon_content = models.TextField(verbose_name="Контент иконки", null=True, blank=True)
    point = PpoiField(
        verbose_name="Точка на генплане", source="project.plan", null=True, blank=True
    )

    project = models.ForeignKey(
        verbose_name="Проект", to="projects.Project", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.name} - {self.project.name}"

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if self.icon:
            with default_storage.open(self.icon.name) as icon_file:
                icon_content = icon_file.read()
                if isinstance(icon_content, bytes):
                    icon_content = icon_content.decode("utf-8")
                icon_content.replace("\n", "").replace("b'", "")
                if icon_content.endswith("'"):
                    icon_content = icon_content[:-1]
            SubInfra.objects.filter(id=self.id).update(icon_content=icon_content)
            self.refresh_from_db()

    class Meta:
        verbose_name = "Дополнительная инфраструктура на генплане"
        verbose_name_plural = "Дополнительные инфраструктуры на генплане"


class RoundInfra(models.Model):
    """
    Окружная инфраструктура на генплане
    """

    name = models.CharField(verbose_name="Название", max_length=100)
    type = models.CharField(verbose_name="Тип", max_length=50, null=True, blank=True)
    add_text = models.CharField(verbose_name="Доп текст", max_length=200, null=True, blank=True)
    color = RGBColorField(verbose_name="Цвет", default="#FFFFFF")
    icon = models.FileField(
        verbose_name="Иконка для списка", blank=True, null=True, upload_to="roundinfra/icon"
    )
    icon_content = models.TextField(verbose_name="Контент иконки", null=True, blank=True)
    point = PpoiField(
        verbose_name="Точка на генплане", source="project.plan", null=True, blank=True
    )
    is_metro = models.BooleanField(verbose_name="Метро", default=False)
    rotation = models.PositiveSmallIntegerField(
        verbose_name="Поворот иконки (в градусах)", default=0
    )
    time = models.CharField(
        verbose_name="Время до инфраструктуры", max_length=100, null=True, blank=True
    )

    project = models.ForeignKey(
        verbose_name="Проект", to="projects.Project", on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if self.icon:
            with default_storage.open(self.icon.name) as icon_file:
                icon_content = icon_file.read()
                if isinstance(icon_content, bytes):
                    icon_content = icon_content.decode("utf-8")
                icon_content.replace("\n", "").replace("b'", "")
                if icon_content.endswith("'"):
                    icon_content = icon_content[:-1]
            RoundInfra.objects.filter(id=self.id).update(icon_content=icon_content)
            self.refresh_from_db()

    def __str__(self) -> str:
        return f"{self.name} - {self.project.name}"

    class Meta:
        verbose_name = "Окружная инфраструктура на генплане"
        verbose_name_plural = "Окружные инфраструктуры на генплане"
