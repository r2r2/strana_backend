# Generated by Django 3.0.10 on 2020-11-30 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("request_forms", "0018_auto_20201126_1406"),
    ]

    operations = [
        migrations.AddField(
            model_name="salerequest",
            name="email",
            field=models.EmailField(blank=True, max_length=200, null=True, verbose_name="Email"),
        ),
    ]
