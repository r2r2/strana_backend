# Generated by Django 3.0.8 on 2020-07-23 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0004_auto_20200722_1429"),
    ]

    operations = [
        migrations.AlterField(
            model_name="furnish",
            name="description",
            field=models.TextField(blank=True, verbose_name="Описание"),
        ),
        migrations.AlterField(
            model_name="furnish",
            name="order",
            field=models.PositiveIntegerField(db_index=True, default=0, verbose_name="Порядок"),
        ),
    ]