# Generated by Django 3.0.14 on 2022-09-05 08:21

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancy', '0002_vacancypageformemployee'),
    ]

    operations = [
        migrations.CreateModel(
            name='VacancyAbout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('desc', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Описание')),
                ('img', models.ImageField(blank=True, null=True, upload_to='f/ip', verbose_name='Изображение')),
                ('button_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Название кнопки')),
                ('link', models.CharField(blank=True, max_length=200, null=True, verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': 'О конпании',
                'verbose_name_plural': 'О компании',
            },
        ),
        migrations.AddField(
            model_name='vacancycategory',
            name='desc',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Текст при наведении на карточку'),
        ),
        migrations.AddField(
            model_name='vacancycategory',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='f/ip', verbose_name='Иконка'),
        ),
        migrations.AlterField(
            model_name='vacancycategory',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Название категории'),
        ),
    ]