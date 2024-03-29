# Generated by Django 3.0.14 on 2022-05-31 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0115_auto_20220531_1226'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='is_angular',
            field=models.BooleanField(default=False, verbose_name='Квартира углавая'),
        ),
        migrations.AddField(
            model_name='property',
            name='is_auction',
            field=models.BooleanField(default=False, verbose_name='Участвует в аукционе'),
        ),
    ]
