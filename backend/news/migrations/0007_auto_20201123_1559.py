# Generated by Django 3.0.10 on 2020-11-23 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_auto_20201123_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='video_length',
            field=models.IntegerField(default=0, help_text='В секундах', verbose_name='Продолжительность видео'),
        ),
        migrations.AddField(
            model_name='newsslide',
            name='video_length',
            field=models.IntegerField(default=0, help_text='В секундах', verbose_name='Продолжительность видео'),
        ),
    ]
