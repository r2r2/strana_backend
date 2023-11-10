from django.db import models


from typing import Optional

class DocumentInteraction(models.Model):
    """
    Взаимодейтвие
    """
    
    name: str = models.CharField(max_length=150, verbose_name="Имя взаимодействия")
    icon = models.FileField(upload_to=None, max_length=350, null=True, verbose_name="Иконка")
    file = models.FileField(upload_to=None, max_length=350)
    priority = models.IntegerField(verbose_name="Приоритет взаимодействия")

    class Meta:
        managed = False
        db_table = "documents_interaction"
        verbose_name = "Взаимодействие"
        verbose_name_plural = "7.11. Взаимодействие"