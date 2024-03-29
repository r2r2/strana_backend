# Generated by Django 3.0.14 on 2022-09-07 09:15

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vacancy', '0005_auto_20220906_1136'),
    ]

    operations = [
        migrations.CreateModel(
            name='VacancyDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('desc', ckeditor.fields.RichTextField(verbose_name='Описание')),
                ('vacancy', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vacancy.Vacancy', verbose_name='Вакансия')),
            ],
            options={
                'verbose_name': 'Описание вакансии',
                'verbose_name_plural': 'Описания вакансии',
            },
        ),
    ]
