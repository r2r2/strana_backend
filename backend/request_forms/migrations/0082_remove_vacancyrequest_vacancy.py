# Generated by Django 3.0.14 on 2022-09-09 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('request_forms', '0081_auto_20220909_1250'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vacancyrequest',
            name='vacancy',
        ),
    ]