# Generated by Django 3.0.10 on 2020-11-19 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contacts", "0006_auto_20201118_0725"),
    ]

    operations = [
        migrations.AddField(
            model_name="office",
            name="is_central",
            field=models.BooleanField(default=False, verbose_name="Центральный"),
        ),
    ]
