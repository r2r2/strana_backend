# Generated by Django 3.0.14 on 2022-09-20 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('request_forms', '0083_auto_20220909_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salerequest',
            name='cadastral_number',
            field=models.CharField(max_length=14, verbose_name='Кадастровый номер'),
        ),
    ]