# Generated by Django 3.0.10 on 2021-08-10 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildings', '0037_merge_20210803_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='total_floor',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество этажей'),
        ),
    ]
