# Generated by Django 3.0.10 on 2020-11-22 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cities', '0015_merge_20201118_0814'),
        ('company', '0017_aboutpage_map_texts'),
    ]

    operations = [
        migrations.CreateModel(
            name='OffersDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='c/od/f', verbose_name='Файл')),
                ('cities', models.ManyToManyField(blank=True, to='cities.City', verbose_name='Города')),
            ],
            options={
                'verbose_name': 'Доументы оферты и политика обработки данных',
                'verbose_name_plural': 'Доументы оферты и политика обработки данных',
            },
        ),
    ]