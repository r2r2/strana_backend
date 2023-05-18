from django.db import models
from django.forms import ValidationError


class ProjectAudience(models.Model):
    """ Модель аудитории проекта """

    commercial_project_page = models.OneToOneField(
        verbose_name="Страница коммерческого проекта",
        to="commercial_project_page.CommercialProjectPage",
        on_delete=models.CASCADE,
    )

    men = models.PositiveSmallIntegerField(verbose_name="Мужчины", help_text="%", default=50)
    women = models.PositiveSmallIntegerField(verbose_name="Женщины", help_text="%", default=50)

    class Meta:
        verbose_name = "Аудитория прокта"
        verbose_name_plural = "Аудитории проектов"

    def __str__(self) -> str:
        return f"Аудитория проекта {self.commercial_project_page.project}"

    def clean(self) -> None:
        if self.men + self.women != 100:
            raise ValidationError("Сумма аудитории мужчин и женщин не равна 100%")


class AudienceIncome(models.Model):
    """ Модель дохода аудитории """

    age = models.CharField(verbose_name="Возраст", max_length=64)
    income = models.PositiveIntegerField(verbose_name="Доход", help_text="тыс. ₽")
    order = models.PositiveSmallIntegerField("Очередность", default=0)
    audience = models.ForeignKey(
        verbose_name="Аудитория проекта", to=ProjectAudience, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("order",)
        verbose_name = "Доход аудитории"
        verbose_name_plural = "Доходы аудитории"

    def __str__(self) -> str:
        return f"{self.age}, {self.income}"


class AudienceFact(models.Model):
    """ Модель факта об аудитории """

    title = models.CharField(verbose_name="Заголовок", max_length=64)
    subtitle = models.CharField(verbose_name="Ползаголовок", max_length=64, blank=True)
    order = models.PositiveSmallIntegerField("Очередность", default=0)
    audience = models.ForeignKey(
        verbose_name="Аудитория проекта", to=ProjectAudience, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("order",)
        verbose_name = "Факт аудитории"
        verbose_name_plural = "Факты аудитории"

    def __str__(self) -> str:
        return self.title


class AudienceAge(models.Model):
    """ Модель возраста аудитории """

    age = models.CharField(verbose_name="Возраст", max_length=64)
    percent = models.PositiveIntegerField(verbose_name="Процент")
    order = models.PositiveSmallIntegerField("Очередность", default=0)
    audience = models.ForeignKey(
        verbose_name="Аудитория проекта", to=ProjectAudience, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("order",)
        verbose_name = "Возраст аудитории"
        verbose_name_plural = "Возраст аудитории"

    def __str__(self) -> str:
        return f"{self.age}, {self.percent}%"
