# Generated by Django 3.0.10 on 2020-10-16 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cities", "0003_metro_metroline_transport"),
    ]

    operations = [
        migrations.AddField(
            model_name="city",
            name="local_coords",
            field=models.TextField(
                blank=True, null=True, verbose_name="Координаты на изображении карты"
            ),
        ),
    ]