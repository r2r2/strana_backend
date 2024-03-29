# Generated by Django 3.0.14 on 2022-05-25 09:03

import common.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buildings', '0052_building_plan_yard'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='yard_point',
            field=common.fields.PpoiField(blank=True, max_length=50, null=True, source='project.plan', verbose_name='Точка дворов и парадной'),
        ),
        migrations.AlterField(
            model_name='building',
            name='plan_yard',
            field=common.fields.PolygonField(blank=True, source='project.plan', verbose_name='Обводка дворов и парадной'),
        ),
    ]
