# Generated by Django 3.0.10 on 2020-09-29 10:34

import ajaximage.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0005_projectadvantage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projectgalleryslide",
            name="image",
            field=ajaximage.fields.AjaxImageField(
                blank=True, null=True, verbose_name="Изображение"
            ),
        ),
    ]
