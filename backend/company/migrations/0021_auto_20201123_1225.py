# Generated by Django 3.0.10 on 2020-11-23 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("company", "0020_largetenant"),
    ]

    operations = [
        migrations.AlterField(
            model_name="largetenant",
            name="logo",
            field=models.FileField(
                blank=True, null=True, upload_to="ap/lt/l", verbose_name="Логотип"
            ),
        ),
    ]
