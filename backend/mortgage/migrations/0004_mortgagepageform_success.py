# Generated by Django 3.0.10 on 2020-11-20 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mortgage", "0003_auto_20201111_1209"),
    ]

    operations = [
        migrations.AddField(
            model_name="mortgagepageform",
            name="success",
            field=models.CharField(
                blank=True, max_length=200, verbose_name="Сообщение при успешной отправке"
            ),
        ),
    ]
