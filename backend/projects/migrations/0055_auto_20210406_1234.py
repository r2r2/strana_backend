# Generated by Django 3.0.10 on 2021-04-06 12:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0054_auto_20210324_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='window_view_plan',
            field=models.ImageField(
                blank=True,
                height_field='window_view_plan_height',
                upload_to='p/p/wvp',
                validators=[django.core.validators.FileExtensionValidator(('jpg', 'jpeg'))],
                verbose_name='План вида из окна',
                width_field='window_view_plan_width',
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='window_view_plan_height',
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name='Высота плана вида из окна'
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='window_view_plan_width',
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name='Ширина плана вида из окна'
            ),
        ),
    ]
