# Generated by Django 3.0.10 on 2020-11-05 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("buildings", "0010_auto_20201105_0740"),
    ]

    operations = [
        migrations.AlterField(
            model_name="building",
            name="kind",
            field=models.CharField(
                choices=[
                    ("living", "Жилое"),
                    ("apartment", "Апартаменты"),
                    ("parking", "Паркинг"),
                    ("commercial", "Коммерческое"),
                ],
                db_index=True,
                default="living",
                max_length=32,
                verbose_name="Тип строения",
            ),
        ),
    ]
