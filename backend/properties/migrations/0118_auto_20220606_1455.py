# Generated by Django 3.0.14 on 2022-06-06 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0117_auto_20220606_1226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='is_angular',
            field=models.BooleanField(default=False, verbose_name='Квартира угловая'),
        ),
    ]