# Generated by Django 3.0.10 on 2021-02-02 15:43

import ajaximage.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0048_auto_20210128_1403'),
        ('request_forms', '0025_reservationlkrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customform',
            name='image',
            field=ajaximage.fields.AjaxImageField(blank=True, null=True, verbose_name='Изображение'),
        ),
        migrations.CreateModel(
            name='CustomFormEmployee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_for_main_page', models.BooleanField(default=False, verbose_name='Показывать на главной странице')),
                ('full_name', models.CharField(max_length=200, verbose_name='ФИО')),
                ('job_title', models.CharField(blank=True, max_length=200, verbose_name='Должность')),
                ('image', ajaximage.fields.AjaxImageField(blank=True, help_text='шир. - 1000, выс. - 906', null=True, verbose_name='Изображение')),
                ('image_phone', models.ImageField(blank=True, null=True, upload_to='f/ip', verbose_name='Мобильное изображение')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='request_forms.CustomForm', verbose_name='Форма')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Project', verbose_name='Проект')),
            ],
            options={
                'verbose_name': 'Сотрудник на кастомой форме',
                'verbose_name_plural': 'Сотрудники кастомных форм',
            },
        ),
    ]