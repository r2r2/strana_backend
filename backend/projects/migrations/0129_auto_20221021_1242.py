# Generated by Django 3.0.14 on 2022-10-21 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0128_auto_20221019_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='header_image',
            field=models.ImageField(blank=True, null=True, upload_to='p/p/fi', verbose_name='Логотип в шапке'),
        ),
        migrations.AddField(
            model_name='project',
            name='header_text',
            field=models.CharField(blank=True, max_length=200, verbose_name='Текст в шапке'),
        ),
        migrations.AddField(
            model_name='project',
            name='header_title',
            field=models.CharField(blank=True, max_length=200, verbose_name='Заголовок в шапке'),
        ),
    ]