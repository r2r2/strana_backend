# Generated by Django 3.0.10 on 2021-09-20 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0082_auto_20210831_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_soon',
            field=models.BooleanField(default=False, help_text='Добавляет текст на карточку', verbose_name='Скоро'),
        ),
    ]