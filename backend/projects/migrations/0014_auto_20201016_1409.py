# Generated by Django 3.0.10 on 2020-10-16 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0013_auto_20201015_0909"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="plan_height",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="Высота генплана"
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="plan_width",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="Ширина генплана"
            ),
        ),
    ]
