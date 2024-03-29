# Generated by Django 3.0.10 on 2021-03-26 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('request_forms', '0037_auto_20210326_0846'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agentrequest',
            name='city',
        ),
        migrations.AddField(
            model_name='agentrequest',
            name='city_name',
            field=models.CharField(blank=True, max_length=64, verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='contractorrequest',
            name='offer',
            field=models.FileField(blank=True, upload_to='request/offer', verbose_name='Коммерческое предложение'),
        ),
    ]
