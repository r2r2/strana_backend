# Generated by Django 3.0.14 on 2021-12-29 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mortgage', '0015_auto_20211229_1209'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
