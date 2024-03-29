# Generated by Django 3.0.10 on 2020-10-16 13:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("buildings", "0004_auto_20200930_1236"),
    ]

    operations = [
        migrations.AddField(
            model_name="building",
            name="compass_azimuth",
            field=models.PositiveSmallIntegerField(
                default=180,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(360),
                ],
                verbose_name="Градус компаса",
            ),
        ),
        migrations.AddField(
            model_name="building",
            name="current_level",
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100),
                ],
                verbose_name="Текущий уровень готовности",
            ),
        ),
    ]
