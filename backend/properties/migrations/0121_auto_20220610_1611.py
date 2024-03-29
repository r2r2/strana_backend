# Generated by Django 3.0.14 on 2022-06-10 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0120_auto_20220608_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='furnish_business_price_per_meter',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, max_digits=14, null=True, verbose_name='Цена с отделкой бизнес за метр'),
        ),
        migrations.AddField(
            model_name='property',
            name='furnish_comfort_price_per_meter',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, max_digits=14, null=True, verbose_name='Цена с отделкой комфорт за метр'),
        ),
    ]
