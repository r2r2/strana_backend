# Generated by Django 3.0.14 on 2021-11-17 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commercial_project_page', '0006_commercialprojectpage_form'),
    ]

    operations = [
        migrations.AddField(
            model_name='commercialprojectpage',
            name='video_preview',
            field=models.ImageField(blank=True, upload_to='cpp/video_preview', verbose_name='Превью для видео'),
        ),
    ]
