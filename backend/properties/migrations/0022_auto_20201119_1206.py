# Generated by Django 3.0.10 on 2020-11-19 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0021_auto_20201116_1045"),
    ]

    operations = [
        migrations.RemoveConstraint(model_name="property", name="unique_property_project_number",),
        migrations.RemoveConstraint(model_name="property", name="unique_property_article",),
        migrations.AddConstraint(
            model_name="property",
            constraint=models.UniqueConstraint(
                condition=models.Q(number__isnull=False),
                fields=("building", "number"),
                name="unique_property_building_number",
            ),
        ),
    ]
