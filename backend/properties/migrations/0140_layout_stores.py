# Generated by Django 3.0.14 on 2022-08-12 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0139_auto_20220811_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='layout',
            name='stores',
            field=models.BooleanField(blank=True, default=False, editable=False, null=True, verbose_name='Кладовые'),
        ),
    ]
