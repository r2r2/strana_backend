# Generated by Django 3.0.8 on 2020-07-20 12:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("buildings", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(model_name="building", old_name="type", new_name="kind",),
    ]