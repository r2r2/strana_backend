# Generated by Django 3.0.10 on 2020-11-16 10:45

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0020_furnish_vr_link"),
    ]

    operations = [
        migrations.CreateModel(
            name="FurnishCategory",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=100, verbose_name="Заголовок")),
                ("text", ckeditor.fields.RichTextField(max_length=1000, verbose_name="Текст")),
                ("order", models.PositiveSmallIntegerField(verbose_name="Порядок")),
            ],
            options={
                "verbose_name": "Категория отделки",
                "verbose_name_plural": "Категории отделки",
                "ordering": ("order",),
            },
        ),
        migrations.AddField(
            model_name="furnishimage",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="image_set",
                to="properties.FurnishCategory",
                verbose_name="Категория",
            ),
        ),
    ]
