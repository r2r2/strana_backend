# Generated by Django 3.0.14 on 2022-07-22 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0127_auto_20220722_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='layout',
            name='is_planoplan',
            field=models.BooleanField(default=False, verbose_name='Виджет от Planoplan'),
        ),
        migrations.AlterField(
            model_name='property',
            name='is_planoplan',
            field=models.BooleanField(default=False, verbose_name='Виджет от Planoplan'),
        ),
    ]