# Generated by Django 3.0.10 on 2021-01-29 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0008_auto_20201205_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='button_link',
            field=models.URLField(blank=True, verbose_name='Ссылка кнопки'),
        ),
        migrations.AddField(
            model_name='news',
            name='button_name',
            field=models.CharField(blank=True, max_length=64, verbose_name='Название кнопки'),
        ),
    ]