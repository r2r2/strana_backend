# Generated by Django 3.0.10 on 2021-01-21 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0029_property_plan_png_preview'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='plan_3d',
            field=models.ImageField(
                blank=True,
                help_text='Добавляется вручную',
                upload_to='pp/i/p3',
                verbose_name='Планировка 3d',
            ),
        ),
    ]
