# Generated by Django 3.0.10 on 2021-04-07 07:36

import common.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0037_auto_20210406_1310'),
    ]

    operations = [
        migrations.CreateModel(
            name='MiniPlanPoint',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'ppoi',
                    common.fields.PpoiField(
                        max_length=50,
                        source='type.building.mini_plan',
                        verbose_name='Точка на мини-плане',
                    ),
                ),
                (
                    'order',
                    models.PositiveIntegerField(db_index=True, default=0, verbose_name='Порядок'),
                ),
                (
                    'type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='properties.WindowViewType',
                        verbose_name='Тип вида из окна',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Точка на миниплане',
                'verbose_name_plural': 'Точки на миниплане',
                'ordering': ('order',),
            },
        ),
        migrations.RemoveField(
            model_name='windowview',
            name='mini_plan_ppoi',
        ),
        migrations.CreateModel(
            name='MiniPlanPointAngle',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'angle',
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(360),
                        ],
                        verbose_name='Угол',
                    ),
                ),
                (
                    'mini_plan',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='properties.MiniPlanPoint',
                        verbose_name='Точка на мини-плане',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Угол обзора на миниплане',
                'verbose_name_plural': 'Углы обзора на миниплане',
            },
        ),
    ]
