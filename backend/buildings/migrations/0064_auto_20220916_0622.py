# Generated by Django 3.0.14 on 2022-09-16 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildings', '0063_auto_20220916_0529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='total_floors',
            field=models.PositiveIntegerField(default=1, verbose_name='Количество этажей'),
            preserve_default=False,
        ),
    ]
