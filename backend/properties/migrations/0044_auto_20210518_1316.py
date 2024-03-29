# Generated by Django 3.0.10 on 2021-05-18 10:16

import common.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("properties", "0043_auto_20210518_1109")]

    operations = [
        migrations.AlterModelOptions(
            name="feature",
            options={
                "ordering": ("order",),
                "verbose_name": "Особенность объекта собственнсти",
                "verbose_name_plural": "Особенности объектов собственности",
            },
        ),
        migrations.RemoveField(model_name="feature", name="properties"),
        migrations.RemoveField(model_name="feature", name="slug"),
        migrations.RemoveField(model_name="property", name="is_disable_online_booking"),
        migrations.AddField(
            model_name="feature",
            name="kind",
            field=models.CharField(
                choices=[
                    ("facing", "Отделка"),
                    ("has_parking", "Паркинг"),
                    ("has_terrace", "Терраса"),
                    ("has_view", "Видовые"),
                    ("has_panoramic_windows", "Панорамные окна"),
                    ("has_two_sides_windows", "Окна на 2 стороны"),
                    ("is_duplex", "Двухуровневая"),
                    ("has_high_ceiling", "Высокий потолок"),
                    ("installment", "Рассрочка"),
                    ("frontage", "Палисадник"),
                    ("preferential_mortgage", "Льготная ипотека"),
                    ("has_tenant", "С арендатором"),
                    ("action", "Акция"),
                    ("favorable_rate", "Выгодная ставка"),
                    ("completed", "Завершенная"),
                ],
                default="facing",
                max_length=48,
                verbose_name="Тип",
            ),
        ),
        migrations.AddField(
            model_name="feature",
            name="order",
            field=models.PositiveSmallIntegerField(
                db_index=True, default=0, verbose_name="Очередность"
            ),
        ),
        migrations.AddField(
            model_name="feature",
            name="property_kind",
            field=common.fields.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("flat", "Квартира"),
                        ("parking", "Парковочное место"),
                        ("commercial", "Коммерческое помещение"),
                        ("pantry", "Кладовка"),
                    ],
                    max_length=20,
                ),
                default=list,
                size=None,
                verbose_name="Типы недвижимости",
            ),
        ),
        migrations.AddField(
            model_name="property",
            name="preferential_mortgage",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="Если true, онлайн-бронирование отключено, на странице лота появляется форма дефолтного бронирования.",
                verbose_name="Льготная ипотека",
            ),
        ),
    ]
