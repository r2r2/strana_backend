# Generated by Django 3.0.14 on 2022-07-08 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0120_project_is_furnish_kitchen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='is_furnish_kitchen',
            field=models.BooleanField(default=False, verbose_name='Отделка кухни'),
        ),
    ]