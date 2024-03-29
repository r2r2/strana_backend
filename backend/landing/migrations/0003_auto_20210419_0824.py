# Generated by Django 3.0.10 on 2021-04-19 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0019_auto_20210413_1343'),
        ('landing', '0002_auto_20210416_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='landingblock',
            name='progress_set',
            field=models.ManyToManyField(blank=True, help_text='Для блока прогресс', limit_choices_to={'type': 'progress'}, to='news.News', verbose_name='Новости ход строительства'),
        ),
        migrations.AlterField(
            model_name='landingblock',
            name='block_type',
            field=models.CharField(choices=[('one_image', 'Блок с текстом и одним изображением'), ('two_image', 'Блок с текстом и двумя изображением'), ('three_image', 'Блок с текстом и тремя изображением'), ('slider', 'Блок со слайдером'), ('simple_cta', 'Простой блок CTA'), ('text_list', 'Блок с текстом и списком'), ('two_column', 'Блок с иконками в две колонки'), ('furnish', 'Блок с отделкой'), ('digits', 'Блок с цифрами'), ('flats', 'Блок квартир'), ('advantage', 'Блок преимуществ'), ('steps', 'Блок шаги'), ('mortgage', 'Блок с ипотекой'), ('progress', 'Ход строительства')], max_length=64, verbose_name='Тип блока'),
        ),
    ]
