# Generated by Django 3.0.10 on 2021-02-24 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0031_auto_20210121_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='hide_price',
            field=models.BooleanField(default=False, verbose_name='Скрыть цену'),
        ),
    ]