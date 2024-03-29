# Generated by Django 3.0.10 on 2020-11-05 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0010_property_favorable_rate"),
    ]

    operations = [
        migrations.AddField(
            model_name="property",
            name="furnish_price",
            field=models.DecimalField(
                blank=True,
                db_index=True,
                decimal_places=2,
                max_digits=14,
                null=True,
                verbose_name="Цена с отделкой",
            ),
        ),
    ]
