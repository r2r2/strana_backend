# Generated by Django 3.0.14 on 2021-12-08 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0085_property_hypo_popular'),
    ]

    operations = [
        migrations.AddField(
            model_name='feature',
            name='is_button',
            field=models.BooleanField(default=False, verbose_name='Выводить кнопкой'),
        ),
    ]