# Generated by Django 3.0.10 on 2021-01-28 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0047_auto_20210128_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectlabel',
            name='description',
            field=models.CharField(blank=True, max_length=300, verbose_name='Описание'),
        ),
    ]