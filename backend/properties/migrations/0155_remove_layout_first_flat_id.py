# Generated by Django 3.0.14 on 2022-11-14 09:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0154_fix_duplicates_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='layout',
            name='first_flat_id',
        ),
    ]
