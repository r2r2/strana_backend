# Generated by Django 3.0.10 on 2020-11-11 11:55

import ajaximage.fields
import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("company", "0014_auto_20201109_1449"),
    ]

    operations = [
        migrations.CreateModel(
            name="VacancyPageForm",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=200, verbose_name="Название")),
                ("title", models.CharField(blank=True, max_length=200, verbose_name="Заголовок")),
                ("description", ckeditor.fields.RichTextField(blank=True, verbose_name="Описание")),
                (
                    "image",
                    ajaximage.fields.AjaxImageField(
                        blank=True,
                        help_text="шир. - 500, выс. - 453",
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
                "verbose_name": "Форма на странице вакансий",
                "verbose_name_plural": "Формы на странице вакансий",
            },
        ),
        migrations.AddField(
            model_name="vacancypage",
            name="form",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="company.VacancyPageForm",
                verbose_name="Форма",
            ),
        ),
    ]
