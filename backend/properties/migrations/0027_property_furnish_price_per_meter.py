# Generated by Django 3.0.10 on 2020-12-23 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0026_auto_20201218_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='furnish_price_per_meter',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, max_digits=14, null=True, verbose_name='Цена с отделкой за метр'),
        ),
    ]
