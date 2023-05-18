from django.db import models
from ckeditor.fields import RichTextField


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


class DevLandAbout(SingletonModel):
    block_name = models.CharField(verbose_name="Название раздела", max_length=255, blank=True, null=True)
    title = models.CharField(verbose_name="Заголовок", max_length=255, blank=True, null=True)
    description = RichTextField(verbose_name="Описание", blank=True, null=True)
    button_name = models.CharField(verbose_name="Надпись на кнопке", max_length=255, blank=True, null=True)
    picture = models.ImageField(max_length=500, blank=True, null=True, upload_to="f/i")

    def __str__(self):
        return f'{self.block_name}'

    class Meta:
        verbose_name = "Информация в шапке"
        verbose_name_plural = "Информация в шапке"


class DevLandBanner(models.Model):
    block_name = models.CharField(verbose_name="Название раздела", max_length=255, blank=True, null=True)
    title = models.CharField(verbose_name="Заголовок", max_length=255, blank=True, null=True)
    description = RichTextField(verbose_name="Описание", blank=True, null=True)
    picture = models.ImageField(max_length=500, blank=True, null=True, upload_to="f/i")

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества"


class DevLandSecondBanner(models.Model):
    main_name = models.CharField(verbose_name="Главное название", max_length=255, blank=True, null=True)
    block_name = models.CharField(verbose_name="Название раздела", max_length=255, blank=True, null=True)
    title = models.CharField(verbose_name="Заголовок", max_length=255, blank=True, null=True)
    years = models.CharField(verbose_name="Годы застройки", max_length=255, blank=True, null=True)
    quadrature = models.CharField(verbose_name="Площадь застройки", max_length=255, blank=True, null=True)
    description = RichTextField(verbose_name="Описание", blank=True, null=True)
    picture = models.ImageField(max_length=500, blank=True, null=True, upload_to="f/i")

    def __str__(self):
        return f'{self.block_name}'

    class Meta:
        verbose_name = "Привмер успешного сотрудничества"
        verbose_name_plural = "Привмеры успешного сотрудничества"


class DevLandThirdBanner(models.Model):
    block_name = models.CharField(verbose_name="Название раздела", max_length=255, blank=True, null=True)
    title = models.CharField(verbose_name="Заголовок", max_length=255, blank=True, null=True)
    subtitle = models.CharField(verbose_name="Заголовок", max_length=255, blank=True, null=True)
    description = RichTextField(verbose_name="Описание", blank=True, null=True)
    picture = models.ImageField(max_length=500, blank=True, null=True, upload_to="f/i")
    button_name = models.CharField(verbose_name="Надпись на кнопке", max_length=255, blank=True, null=True)
    button_link = models.CharField(verbose_name="Надпись на кнопке", max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.block_name}'

    class Meta:
        verbose_name = "Партнерская программа"
        verbose_name_plural = "Партнерские программы"


class DevLandImages(models.Model):
    icon = models.ImageField(max_length=500, blank=True, null=True, upload_to="f/i")
    partner = models.OneToOneField(DevLandThirdBanner, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = "Картинка бля блоока партнерская программа"
        verbose_name_plural = "Картинка бля блоока партнерская программа"


class DevLandCheckBoxesTitle(SingletonModel):
    title = models.CharField(verbose_name="Заголовок", max_length=255, blank=True, null=True)
    button_name = models.CharField(verbose_name="Надпись на кнопке", max_length=255, blank=True, null=True)
    button_link = models.CharField(verbose_name="Ссылка на кнопке", max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = "Описание чекбоксов"
        verbose_name_plural = "Описание чекбоксов"


class DevLandCheckBoxes(models.Model):
    icon = models.ImageField(max_length=500, blank=True, null=True, upload_to="f/i")
    title = models.CharField(verbose_name="Заголовок", max_length=255, blank=True, null=True)
    description = RichTextField(verbose_name="Описание", blank=True, null=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = "Чекбокс"
        verbose_name_plural = "Чекбоксы"


class DevLandMap(SingletonModel):
    title = models.CharField(verbose_name="Заголовок", max_length=255, blank=True, null=True)
    description = RichTextField(verbose_name="Описание", blank=True, null=True)
    number_1 = models.PositiveIntegerField(verbose_name='Число 1', blank=True, null=True)
    number_2 = models.PositiveIntegerField(verbose_name='Число 2', blank=True, null=True)
    number_3 = models.PositiveIntegerField(verbose_name='Число 3', blank=True, null=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = "Данные на карте"
        verbose_name_plural = "Данные на карте"
