# Generated by Django 3.0.10 on 2020-11-13 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0016_propertycard"),
    ]

    operations = [
        migrations.AddField(
            model_name="furnishpoint",
            name="title",
            field=models.CharField(blank=True, max_length=100, verbose_name="Заголовок"),
        ),
    ]
