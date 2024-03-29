# Generated by Django 3.0.10 on 2020-11-11 12:09

import ajaximage.fields
import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("mortgage", "0002_auto_20201106_0616"),
    ]

    operations = [
        migrations.CreateModel(
            name="MortgagePageForm",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=200, verbose_name="Заголовок")),
                ("description", ckeditor.fields.RichTextField(blank=True, verbose_name="Описание")),
                (
                    "image",
                    ajaximage.fields.AjaxImageField(
                        blank=True,
                        help_text="шир. - 500, выс. - 440",
                        null=True,
                        verbose_name="Изображение",
                    ),
                ),
                (
                    "button_text",
                    models.CharField(blank=True, max_length=200, verbose_name="Текст на кнопке"),
                ),
                ("full_name", models.CharField(blank=True, max_length=200, verbose_name="ФИО")),
                (
                    "job_title",
                    models.CharField(blank=True, max_length=200, verbose_name="Должность"),
                ),
            ],
            options={
                "verbose_name": "Форма на странице ипотеки",
                "verbose_name_plural": "Формы на странице ипотеки",
            },
        ),
        migrations.AddField(
            model_name="mortgagepage",
            name="form",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="mortgage.MortgagePageForm",
                verbose_name="Форма",
            ),
        ),
    ]
