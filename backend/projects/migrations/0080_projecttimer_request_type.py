# Generated by Django 3.0.10 on 2021-08-03 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0079_auto_20210803_1136"),
    ]

    operations = [
        migrations.AddField(
            model_name="projecttimer",
            name="request_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("callback", "Заявка на обратный звонок"),
                    ("excursion", "Запись на экскурсию"),
                ],
                max_length=32,
                verbose_name="Тип формы",
            ),
        ),
    ]
