# Generated by Django 3.0.10 on 2020-11-26 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("request_forms", "0016_auto_20201122_1254"),
    ]

    operations = [
        migrations.AddField(
            model_name="customform",
            name="image_mobile",
            field=models.ImageField(
                blank=True, null=True, upload_to="f/ip", verbose_name="Мобильное изображение"
            ),
        ),
    ]
