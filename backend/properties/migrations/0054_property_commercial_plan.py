# Generated by Django 3.0.10 on 2021-06-29 12:30

import ajaximage.fields
import django.core.validators
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("properties", "0053_auto_20210624_1834")]

    operations = [
        migrations.AddField(
            model_name="property",
            name="commercial_plan",
            field=ajaximage.fields.AjaxImageField(
                blank=True,
                help_text="Для фильтра коммерции",
                validators=[django.core.validators.FileExtensionValidator(("png", "svg"))],
                verbose_name="Планировка апартаментов коммерции",
            ),
        )
    ]
