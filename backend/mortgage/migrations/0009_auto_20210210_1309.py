# Generated by Django 3.0.10 on 2021-02-10 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mortgage', '0008_auto_20201211_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='mortgageadvantage',
            name='min_value',
            field=models.FloatField(blank=True, null=True, verbose_name='Мин ставка'),
        ),
        migrations.AddField(
            model_name='mortgagepage',
            name='min_value',
            field=models.FloatField(blank=True, null=True, verbose_name='Мин ставка'),
        ),
    ]