# Generated by Django 3.0.10 on 2021-09-22 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cities', '0024_city_is_without_lots'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='is_only_map',
            field=models.BooleanField(default=False, verbose_name='Отображать город только на карте'),
        ),
        migrations.AddField(
            model_name='city',
            name='is_region',
            field=models.BooleanField(default=False, help_text='Скрывает на карте', verbose_name='Область'),
        ),
        migrations.AddField(
            model_name='city',
            name='map_name',
            field=models.CharField(blank=True, max_length=128, verbose_name='Название на карте'),
        ),
    ]
