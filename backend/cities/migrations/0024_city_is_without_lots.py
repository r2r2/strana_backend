# Generated by Django 3.0.10 on 2021-09-21 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cities', '0023_city_disable_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='is_without_lots',
            field=models.BooleanField(default=False, help_text='Скрывает функционал на фронте', verbose_name='Город без лотов'),
        ),
    ]