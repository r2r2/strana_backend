# Generated by Django 3.0.14 on 2022-06-30 10:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0122_propertymap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propertymap',
            name='property',
            field=models.ForeignKey(limit_choices_to={'type': 'commercial'}, on_delete=django.db.models.deletion.CASCADE, to='properties.Property', verbose_name='Объект собственности'),
        ),
    ]
