# Generated by Django 3.0.14 on 2022-08-16 13:34

import common.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0005_auto_20220816_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feed',
            name='template_type',
            field=common.fields.ChoiceArrayField(base_field=models.CharField(choices=[('yandex', 'Яндекс'), ('cian', 'Циан'), ('avito', 'Авито')], max_length=20), default=list, size=None, verbose_name='Типы шаблонов'),
        ),
    ]