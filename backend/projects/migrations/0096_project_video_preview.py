# Generated by Django 3.0.14 on 2021-11-15 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0095_project_show_close'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='video_preview',
            field=models.ImageField(blank=True, null=True, upload_to='p/video_preview', verbose_name='Превью видео'),
        ),
    ]
