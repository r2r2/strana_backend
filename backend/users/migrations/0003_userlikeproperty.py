# Generated by Django 3.0.14 on 2022-02-09 15:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0110_merge_20220208_1538"),
        ("users", "0002_searchquery"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserLikeProperty",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("date", models.DateTimeField(auto_now=True, verbose_name="Дата добавления")),
                (
                    "property",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="properties.Property",
                        verbose_name="Помещение",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "ordering": ("-date",),
                "unique_together": {("user", "property")},
            },
        ),
    ]
