# Generated by Django 3.0.14 on 2022-07-18 14:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0016_auto_20220718_1727'),
    ]

    operations = [
        migrations.RenameField(
            model_name='investmenttypes',
            old_name='checkin',
            new_name='priority',
        ),
        migrations.RenameField(
            model_name='rentalbusinesssales',
            old_name='checkin',
            new_name='priority',
        ),
        migrations.RenameField(
            model_name='yieldcomparison',
            old_name='checkin',
            new_name='priority',
        ),
    ]
