# Generated by Django 3.0.10 on 2020-11-02 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cities", "0006_auto_20201029_1214"),
    ]

    operations = [
        migrations.AddField(
            model_name="city",
            name="latitude",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=9, null=True, verbose_name="Широта"
            ),
        ),
        migrations.AddField(
            model_name="city",
            name="longitude",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=9, null=True, verbose_name="Долгота"
            ),
        ),
    ]