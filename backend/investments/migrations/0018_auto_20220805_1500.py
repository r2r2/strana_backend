# Generated by Django 3.0.14 on 2022-08-05 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0017_auto_20220718_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investmenttypes',
            name='management_complexity',
            field=models.CharField(choices=[('Легко', 'easy'), ('Средняя', 'medium'), ('Сложно', 'hard')], max_length=255, verbose_name='Легкость в управлении'),
        ),
    ]
