# Generated by Django 3.0.10 on 2020-10-27 08:43

import common.fields
from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ("request_forms", "0005_auto_20201020_0903"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReservationRequest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Имя")),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None, verbose_name="Номер"
                    ),
                ),
                (
                    "date",
                    models.DateTimeField(auto_now_add=True, verbose_name="Дата и время отправки"),
                ),
            ],
            options={
                "verbose_name": "Заявка на бронирование",
                "verbose_name_plural": "Заявки на бронирование",
                "ordering": ("-date",),
            },
        ),
        migrations.AlterField(
            model_name="manager",
            name="type_list",
            field=common.fields.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("vacancy", "Отклик на вакансию"),
                        ("sale", "Заявка на продажу участка"),
                        ("callback", "Заявка на обратный звонок"),
                        ("reservation", "Заявка на бронирование"),
                        ("excursion", "Запись на экскурсию"),
                        ("director", "Запрос на связь с директором"),
                    ],
                    max_length=20,
                ),
                size=None,
                verbose_name="Типы заявок",
            ),
        ),
    ]
