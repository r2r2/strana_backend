# Generated by Django 3.0.10 on 2020-11-02 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0009_furnishpoint"),
    ]

    operations = [
        migrations.AddField(
            model_name="property",
            name="favorable_rate",
            field=models.BooleanField(default=False, verbose_name="Выгодная ставка"),
        ),
    ]
