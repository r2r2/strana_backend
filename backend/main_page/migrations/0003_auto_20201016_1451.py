# Generated by Django 3.0.10 on 2020-10-16 14:51

import ajaximage.fields
import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main_page", "0002_auto_20201016_1419"),
    ]

    operations = [
        migrations.AddField(
            model_name="mainpage",
            name="side_block_hover_text_1",
            field=ckeditor.fields.RichTextField(
                blank=True, verbose_name="Боковой блок 1 / Текст при ховере"
            ),
        ),
        migrations.AddField(
            model_name="mainpage",
            name="side_block_hover_text_2",
            field=ckeditor.fields.RichTextField(
                blank=True, verbose_name="Боковой блок 2 / Текст при ховере"
            ),
        ),
        migrations.AddField(
            model_name="mainpage",
            name="side_block_image_1",
            field=ajaximage.fields.AjaxImageField(
                blank=True, null=True, verbose_name="Боковой блок 1 / Изображение"
            ),
        ),
        migrations.AddField(
            model_name="mainpage",
            name="side_block_image_2",
            field=ajaximage.fields.AjaxImageField(
                blank=True, null=True, verbose_name="Боковой блок 2 / Изображение"
            ),
        ),
        migrations.AddField(
            model_name="mainpage",
            name="side_block_text_1",
            field=ckeditor.fields.RichTextField(blank=True, verbose_name="Боковой блок 1 / Текст"),
        ),
        migrations.AddField(
            model_name="mainpage",
            name="side_block_text_2",
            field=ckeditor.fields.RichTextField(blank=True, verbose_name="Боковой блок 2 / Текст"),
        ),
        migrations.AddField(
            model_name="mainpage",
            name="side_block_title_1",
            field=models.CharField(
                blank=True, max_length=200, verbose_name="Боковой блок 1 / Заголовок"
            ),
        ),
        migrations.AddField(
            model_name="mainpage",
            name="side_block_title_2",
            field=models.CharField(
                blank=True, max_length=200, verbose_name="Боковой блок 2 / Заголовок"
            ),
        ),
    ]
