# Generated by Django 3.0.10 on 2021-01-27 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0042_auto_20210127_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='bank_logo_1',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Лого банка 1'),
        ),
        migrations.AddField(
            model_name='project',
            name='bank_logo_2',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Лого банка 2'),
        ),
    ]
