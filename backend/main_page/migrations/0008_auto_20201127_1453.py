# Generated by Django 3.0.10 on 2020-11-27 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main_page", "0007_auto_20201127_1441"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mainpageslide",
            name="button_link",
            field=models.CharField(blank=True, max_length=100, verbose_name="Ссылка на кнопке"),
        ),
    ]
