# Generated by Django 3.0.10 on 2021-06-16 08:20

import common.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("request_forms", "0046_merge_20210611_1437")]

    operations = [
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
                        ("teaser", "Заявка со слайда главной страницы (тизера)"),
                    ],
                    max_length=20,
                ),
                size=None,
                verbose_name="Типы заявок",
            ),
        )
    ]