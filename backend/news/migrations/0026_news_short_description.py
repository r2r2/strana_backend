# Generated by Django 3.0.10 on 2021-07-16 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("news", "0025_auto_20210623_1859")]

    operations = [
        migrations.AddField(
            model_name="news",
            name="short_description",
            field=models.TextField(
                blank=True, help_text="Для страницы проекта", verbose_name="Краткое описание"
            ),
        )
    ]