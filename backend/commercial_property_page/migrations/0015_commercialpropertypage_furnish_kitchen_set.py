# Generated by Django 3.0.14 on 2022-07-08 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0125_auto_20220708_0936'),
        ('commercial_property_page', '0014_merge_20210316_1017'),
    ]

    operations = [
        migrations.AddField(
            model_name='commercialpropertypage',
            name='furnish_kitchen_set',
            field=models.ManyToManyField(blank=True, to='properties.FurnishKitchen', verbose_name='Варианты отделки кухни'),
        ),
    ]
