# Generated by Django 3.0.10 on 2021-09-20 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0071_merge_20210917_1636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='repair_color_object',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='properties.RepairColor', verbose_name='Цвет ремонта(выбор)'),
        ),
    ]
