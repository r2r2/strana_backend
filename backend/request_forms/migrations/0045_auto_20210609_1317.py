# Generated by Django 3.0.10 on 2021-06-09 10:17

import common.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("request_forms", "0044_merge_20210528_1442")]

    operations = [
        migrations.CreateModel(
            name="AntiCorruptionRequest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Имя")),
                (
                    "email",
                    models.EmailField(blank=True, max_length=200, null=True, verbose_name="Email"),
                ),
                ("message", models.TextField(blank=True, verbose_name="Сообщение")),
                (
                    "date",
                    models.DateTimeField(auto_now_add=True, verbose_name="Дата и время отправки"),
                ),
            ],
            options={
                "verbose_name": "Заявка о противодействии коррупции",
                "verbose_name_plural": "Заявки о противодействии коррупции",
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
                        ("purchase", "Заявка на помощь с оформлением покупки"),
                        ("agent", "Заявка агентств"),
                        ("Contractor", "Заявки для подрядчиков"),
                        ("custom", "Кастомная заявка"),
                        ("commercial_rent", "Заявка на аренду коммерческого помещения"),
                        ("media", "Заявка для СМИ"),
                        ("realty_update", "Обновление недвижимости"),
                        ("anti_corruption", "Заявка о противодействии коррупции"),
                    ],
                    max_length=20,
                ),
                size=None,
                verbose_name="Типы заявок",
            ),
        ),
    ]
