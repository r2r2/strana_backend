# Generated by Django 3.0.10 on 2021-11-01 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0094_auto_20211026_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='show_close',
            field=models.BooleanField(default=True, verbose_name="Отображать в фильтре квартир 'ближ.'"),
        ),
    ]
