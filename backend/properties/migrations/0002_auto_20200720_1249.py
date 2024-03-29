# Generated by Django 3.0.8 on 2020-07-20 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="property",
            name="type",
            field=models.CharField(
                choices=[
                    ("flat", "Квартира"),
                    ("parking", "Парковочное место"),
                    ("commercial", "Коммерческое помещение"),
                    ("pantry", "Кладовка"),
                ],
                db_index=True,
                max_length=20,
                verbose_name="Тип",
            ),
        ),
    ]
