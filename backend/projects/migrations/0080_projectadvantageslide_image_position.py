# Generated by Django 3.0.10 on 2021-08-06 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0079_auto_20210804_1205"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectadvantageslide",
            name="image_position",
            field=models.CharField(
                choices=[
                    ("left", "Слева"),
                    ("right", "Справа"),
                    ("center", "Центр"),
                    ("bottom", "Снизу"),
                ],
                default="center",
                max_length=20,
                verbose_name="Положение изображения",
            ),
        ),
    ]