# Generated by Django 3.0.14 on 2022-07-06 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0008_auto_20220705_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='investmenttypes',
            name='checkin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='investmenttypes',
            name='risks_alt',
            field=models.CharField(default=1, max_length=255, verbose_name='Описание рисков'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='yieldcomparison',
            name='quadrature',
            field=models.FloatField(default=1, verbose_name='Квадратура'),
            preserve_default=False,
        ),
    ]