# Generated by Django 3.0.14 on 2021-11-16 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('request_forms', '0066_auto_20211027_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='callbackrequest',
            name='timezone_user',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]