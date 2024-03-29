# Generated by Django 3.0.8 on 2020-07-21 12:53

import ajaximage.fields
import common.fields
import django.core.validators
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("buildings", "0002_auto_20200720_1249"),
    ]

    operations = [
        migrations.AddField(
            model_name="building",
            name="plan",
            field=ajaximage.fields.AjaxImageField(
                blank=True,
                validators=[django.core.validators.FileExtensionValidator(("jpg", "jpeg"))],
                verbose_name="Планировка",
            ),
        ),
        migrations.AddField(
            model_name="building",
            name="plan_hover",
            field=common.fields.PolygonField(
                blank=True, source="project.plan", verbose_name="Обводка на генплане"
            ),
        ),
        migrations.AddField(
            model_name="floor",
            name="plan",
            field=ajaximage.fields.AjaxImageField(
                blank=True,
                validators=[django.core.validators.FileExtensionValidator(("svg",))],
                verbose_name="Планировка",
            ),
        ),
        migrations.AddField(
            model_name="floor",
            name="plan_hover",
            field=common.fields.PolygonField(
                blank=True, source="section.plan", verbose_name="Обводка на плане"
            ),
        ),
        migrations.AddField(
            model_name="section",
            name="plan",
            field=ajaximage.fields.AjaxImageField(
                blank=True,
                validators=[django.core.validators.FileExtensionValidator(("png", "svg"))],
                verbose_name="Планировка",
            ),
        ),
        migrations.AddField(
            model_name="section",
            name="plan_hover",
            field=common.fields.PolygonField(
                blank=True, source="building.plan", verbose_name="Обводка на плане"
            ),
        ),
    ]
