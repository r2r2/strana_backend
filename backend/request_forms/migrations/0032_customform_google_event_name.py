# Generated by Django 3.0.10 on 2021-03-04 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('request_forms', '0031_auto_20210301_0832'),
    ]

    operations = [
        migrations.AddField(
            model_name='customform',
            name='google_event_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Название ивента Google'),
        ),
    ]