# Generated by Django 3.0.10 on 2021-08-23 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0063_auto_20210729_1856'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListingAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, verbose_name='Заголовок')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Очередность')),
                ('image', models.ImageField(blank=True, help_text='Ширина: 400, высота: 600', upload_to='p/la', verbose_name='Изображенине')),
                ('button_name', models.CharField(blank=True, max_length=64, verbose_name='Название кнопки')),
                ('button_link', models.CharField(blank=True, max_length=255, verbose_name='Ссылка кнопки')),
            ],
            options={
                'verbose_name': 'Акция в листинге квартир',
                'verbose_name_plural': 'Акции в листинге квартир',
                'ordering': ('order',),
            },
        ),
    ]