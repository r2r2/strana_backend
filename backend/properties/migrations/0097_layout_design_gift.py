# Generated by Django 3.0.10 on 2022-01-17 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0096_auto_20220117_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='layout',
            name='design_gift',
            field=models.BooleanField(default=False, verbose_name='Дизайн-проект в подарок'),
        ),
    ]
