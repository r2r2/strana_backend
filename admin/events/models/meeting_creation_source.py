from django.db import models


# deprecated
class MeetingCreationSource(models.Model):
    """
    Таблица источника создания встречи.
    """

    slug = models.CharField(verbose_name='Слаг', max_length=20, unique=True)
    label = models.CharField(verbose_name='Название источника создания встречи', max_length=40)

    def __str__(self):
        return self.label

    class Meta:
        managed = False
        db_table = "meetings_meeting_creation_source"
        verbose_name = "Источник создания встречи"
        verbose_name_plural = "8.6. [Справочник] Источники создания встречи Deprecated"


class MeetingCreationSourceRef(models.Model):
    """
    Таблица источника создания встречи.
    """

    slug = models.CharField(verbose_name='Слаг', max_length=20, primary_key=True)
    label = models.CharField(verbose_name='Название источника создания встречи', max_length=40)

    def __str__(self):
        return self.label

    class Meta:
        managed = False
        db_table = "meetings_meeting_creation_source_ref"
        verbose_name = "Источник создания встречи"
        verbose_name_plural = "8.6. [Справочник] Источники создания встречи"
