# Generated by Django 3.0.10 on 2021-10-14 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0088_merge_20211008_1746'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_display_future_on_map',
            field=models.BooleanField(default=False, verbose_name='Выводить будущий проект на карту'),
        ),
    ]
