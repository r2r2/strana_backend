# Generated by Django 3.0.10 on 2020-11-11 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0015_property_action"),
        ("request_forms", "0011_auto_20201111_0914"),
    ]

    operations = [
        migrations.AddField(
            model_name="customrequest",
            name="property",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="properties.Property",
                verbose_name="Объект собственности",
            ),
        ),
    ]
