# Generated by Django 3.0.14 on 2022-07-08 07:07

import ajaximage.fields
import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0012_auto_20220707_1435'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='owneyelooking',
            name='button_link',
        ),
        migrations.RemoveField(
            model_name='owneyelooking',
            name='button_name',
        ),
        migrations.RemoveField(
            model_name='owneyelooking',
            name='img_description',
        ),
        migrations.RemoveField(
            model_name='owneyelooking',
            name='picture',
        ),
        migrations.RemoveField(
            model_name='owneyelooking',
            name='subtitle',
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='active',
            field=models.BooleanField(default=False, verbose_name='Активна'),
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='button_text',
            field=models.CharField(blank=True, max_length=200, verbose_name='Текст на кнопке'),
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='description',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='full_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='ФИО'),
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='google_event_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Название ивента Google'),
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='image',
            field=ajaximage.fields.AjaxImageField(blank=True, null=True, verbose_name='Изображение'),
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='image_phone',
            field=models.ImageField(blank=True, null=True, upload_to='f/ip', verbose_name='Мобильное изображение'),
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='job_title',
            field=models.CharField(blank=True, max_length=200, verbose_name='Должность'),
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='name',
            field=models.CharField(default=1, max_length=200, verbose_name='Название'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='order',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Порядок'),
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='success',
            field=models.CharField(blank=True, max_length=200, verbose_name='Сообщение при успешной отправке'),
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='type_form',
            field=models.CharField(blank=True, max_length=200, verbose_name='Тип для обработки запроса'),
        ),
        migrations.AddField(
            model_name='owneyelooking',
            name='yandex_metrics',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Яндекс метрика'),
        ),
        migrations.AlterField(
            model_name='owneyelooking',
            name='title',
            field=models.CharField(blank=True, default=1, max_length=200, verbose_name='Заголовок'),
            preserve_default=False,
        ),
    ]