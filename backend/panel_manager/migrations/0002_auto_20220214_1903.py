# Generated by Django 3.0.14 on 2022-02-14 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='meeting_end_type',
            field=models.IntegerField(blank=True, choices=[(1, 'Встреча назначена'), (2, 'Идет встреча'), (3, 'Принимают решение'), (4, 'Повторная встреча'), (5, 'Бронь'), (6, 'Отказ')], null=True, verbose_name='Тип окончания сделки'),
        ),
    ]