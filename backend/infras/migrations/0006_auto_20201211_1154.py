# Generated by Django 3.0.10 on 2020-12-11 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("infras", "0005_auto_20201030_1406"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="infra",
            options={
                "verbose_name": "Инфраструктура на карте",
                "verbose_name_plural": "Инфраструктуры на карте",
            },
        ),
        migrations.AlterModelOptions(
            name="infracategory",
            options={
                "ordering": ("order",),
                "verbose_name": "Категория инфраструктуры на карте",
                "verbose_name_plural": "Категории инфраструктуры на карте",
            },
        ),
        migrations.AlterModelOptions(
            name="infracontent",
            options={
                "verbose_name": "Контент инфраструктуры на карте",
                "verbose_name_plural": "Контенты инфраструктуры на карте",
            },
        ),
        migrations.AlterModelOptions(
            name="infratype",
            options={
                "ordering": ("order",),
                "verbose_name": "Тип инфраструктуры на карте",
                "verbose_name_plural": "Типы инфраструктуры на карте",
            },
        ),
        migrations.AlterModelOptions(
            name="maininfra",
            options={
                "verbose_name": "Главная инфраструктура на генплане",
                "verbose_name_plural": "Главные инфраструктуры на генплане",
            },
        ),
        migrations.AlterModelOptions(
            name="maininfracontent",
            options={
                "verbose_name": "Контент главной инфраструктуры",
                "verbose_name_plural": "Контенты главной инфраструктуры",
            },
        ),
        migrations.AlterModelOptions(
            name="roundinfra",
            options={
                "verbose_name": "Окружная инфраструктура на генплане",
                "verbose_name_plural": "Окружные инфраструктуры на генплане",
            },
        ),
        migrations.AlterModelOptions(
            name="subinfra",
            options={
                "verbose_name": "Дополнительная инфраструктура на генплане",
                "verbose_name_plural": "Дополнительные инфраструктуры на генплане",
            },
        ),
    ]
