# Generated by Django 3.0.10 on 2020-09-28 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0003_auto_20200928_1306"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectGallerySlide",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="", verbose_name="Изображение"
                    ),
                ),
                ("video_link", models.URLField(blank=True, verbose_name="Ссылка на видео"),),
                (
                    "order",
                    models.PositiveSmallIntegerField(
                        db_index=True, default=0, verbose_name="Порядок"
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="gallery_slides",
                        to="projects.Project",
                    ),
                ),
            ],
            options={
                "verbose_name": "Слайд галлереи",
                "verbose_name_plural": "Слайды галлереи",
                "ordering": ("order",),
            },
        ),
    ]
