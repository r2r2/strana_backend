# Generated by Django 3.0.10 on 2021-02-25 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commercial_property_page', '0009_commercialrentform'),
    ]

    operations = [
        migrations.AddField(
            model_name='commercialpropertypage',
            name='is_page_hidden',
            field=models.BooleanField(default=False, verbose_name='Скрыть страницу для отображения'),
        ),
    ]
