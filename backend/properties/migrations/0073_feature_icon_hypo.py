# Generated by Django 3.0.10 on 2021-09-24 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0072_auto_20210920_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='feature',
            name='icon_hypo',
            field=models.FileField(blank=True, help_text='Загружать изображение около 300x250px', upload_to='p/ph', verbose_name='Иконка для гипотезы'),
        ),
    ]
