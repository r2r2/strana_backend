# Generated by Django 3.0.14 on 2022-02-17 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel_manager', '0004_auto_20220216_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='meeting_end_type',
            field=models.IntegerField(blank=True, choices=[(3, 'Принимает решение'), (4, 'Повторная встреча'), (5, 'Бронь'), (6, 'Отказ')], null=True, verbose_name='Тип окончания сделки'),
        ),
    ]
