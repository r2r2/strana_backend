# Generated by Django 3.0.10 on 2021-05-28 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("request_forms", "0042_auto_20210519_1151")]

    operations = [
        migrations.AlterField(
            model_name="agentrequest",
            name="property_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("flat", "Квартира"),
                    ("parking", "Парковочное место"),
                    ("commercial", "Коммерческое помещение"),
                    ("pantry", "Кладовка"),
                    ("commercial_apartment", "Аппартаменты коммерции"),
                ],
                max_length=20,
                verbose_name="Тип",
            ),
        ),
        migrations.AlterField(
            model_name="callbackrequest",
            name="property_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("flat", "Квартира"),
                    ("parking", "Парковочное место"),
                    ("commercial", "Коммерческое помещение"),
                    ("pantry", "Кладовка"),
                    ("commercial_apartment", "Аппартаменты коммерции"),
                ],
                max_length=20,
                verbose_name="Тип",
            ),
        ),
        migrations.AlterField(
            model_name="commercialrentrequest",
            name="property_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("flat", "Квартира"),
                    ("parking", "Парковочное место"),
                    ("commercial", "Коммерческое помещение"),
                    ("pantry", "Кладовка"),
                    ("commercial_apartment", "Аппартаменты коммерции"),
                ],
                max_length=20,
                verbose_name="Тип",
            ),
        ),
        migrations.AlterField(
            model_name="contractorrequest",
            name="property_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("flat", "Квартира"),
                    ("parking", "Парковочное место"),
                    ("commercial", "Коммерческое помещение"),
                    ("pantry", "Кладовка"),
                    ("commercial_apartment", "Аппартаменты коммерции"),
                ],
                max_length=20,
                verbose_name="Тип",
            ),
        ),
        migrations.AlterField(
            model_name="customrequest",
            name="property_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("flat", "Квартира"),
                    ("parking", "Парковочное место"),
                    ("commercial", "Коммерческое помещение"),
                    ("pantry", "Кладовка"),
                    ("commercial_apartment", "Аппартаменты коммерции"),
                ],
                max_length=20,
                verbose_name="Тип",
            ),
        ),
        migrations.AlterField(
            model_name="directorcommunicaterequest",
            name="property_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("flat", "Квартира"),
                    ("parking", "Парковочное место"),
                    ("commercial", "Коммерческое помещение"),
                    ("pantry", "Кладовка"),
                    ("commercial_apartment", "Аппартаменты коммерции"),
                ],
                max_length=20,
                verbose_name="Тип",
            ),
        ),
        migrations.AlterField(
            model_name="excursionrequest",
            name="property_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("flat", "Квартира"),
                    ("parking", "Парковочное место"),
                    ("commercial", "Коммерческое помещение"),
                    ("pantry", "Кладовка"),
                    ("commercial_apartment", "Аппартаменты коммерции"),
                ],
                max_length=20,
                verbose_name="Тип",
            ),
        ),
        migrations.AlterField(
            model_name="purchasehelprequest",
            name="property_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("flat", "Квартира"),
                    ("parking", "Парковочное место"),
                    ("commercial", "Коммерческое помещение"),
                    ("pantry", "Кладовка"),
                    ("commercial_apartment", "Аппартаменты коммерции"),
                ],
                max_length=20,
                verbose_name="Тип",
            ),
        ),
        migrations.AlterField(
            model_name="reservationlkrequest",
            name="property_type",
            field=models.CharField(
                choices=[
                    ("flat", "Квартира"),
                    ("parking", "Парковочное место"),
                    ("commercial", "Коммерческое помещение"),
                    ("pantry", "Кладовка"),
                    ("commercial_apartment", "Аппартаменты коммерции"),
                ],
                max_length=20,
                verbose_name="Тип",
            ),
        ),
        migrations.AlterField(
            model_name="reservationrequest",
            name="property_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("flat", "Квартира"),
                    ("parking", "Парковочное место"),
                    ("commercial", "Коммерческое помещение"),
                    ("pantry", "Кладовка"),
                    ("commercial_apartment", "Аппартаменты коммерции"),
                ],
                max_length=20,
                verbose_name="Тип",
            ),
        ),
    ]