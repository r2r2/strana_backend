# Generated by Django 3.0.8 on 2020-09-25 10:41

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("cities", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Office",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID",
                    ),
                ),
                (
                    "active",
                    models.BooleanField(db_index=True, default=True, verbose_name="Активный"),
                ),
                ("name", models.CharField(blank=True, max_length=200, verbose_name="Название"),),
                ("address", models.CharField(blank=True, max_length=200, verbose_name="Адрес"),),
                (
                    "latitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        max_digits=9,
                        null=True,
                        verbose_name="Широта",
                    ),
                ),
                (
                    "longitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        max_digits=9,
                        null=True,
                        verbose_name="Долгота",
                    ),
                ),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None, verbose_name="Телефон",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="Адрес электронной почты",
                    ),
                ),
                (
                    "work_time",
                    models.CharField(blank=True, max_length=200, verbose_name="Часы работы"),
                ),
                ("comment", models.TextField(blank=True, verbose_name="Комментарий")),
                (
                    "city",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cities.City",
                        verbose_name="Город",
                    ),
                ),
            ],
            options={"verbose_name": "Офис", "verbose_name_plural": "Офисы",},
        ),
        migrations.CreateModel(
            name="Subdivision",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID",
                    ),
                ),
                (
                    "active",
                    models.BooleanField(db_index=True, default=True, verbose_name="Активный"),
                ),
                ("name", models.CharField(blank=True, max_length=200, verbose_name="Название"),),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None, verbose_name="Телефон",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="Адрес электронной почты",
                    ),
                ),
                (
                    "office",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contacts.Office",
                        verbose_name="Офис",
                    ),
                ),
            ],
            options={"verbose_name": "Подразделение", "verbose_name_plural": "Подразделения",},
        ),
    ]