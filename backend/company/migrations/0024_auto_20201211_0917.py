# Generated by Django 3.0.10 on 2020-12-11 09:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("company", "0023_vacancypageform_yandex_metrics"),
    ]

    operations = [
        migrations.AlterField(
            model_name="partnerspageblock",
            name="block_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("bank", "Банк"),
                    ("agent", "Агент"),
                    ("contractor", "Подрядчик"),
                    ("sale_plot", "Продажа земельного участка"),
                ],
                max_length=300,
                verbose_name="Тип блока",
            ),
        ),
        migrations.AlterField(
            model_name="vacancypageadvantage",
            name="page",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="company.VacancyPage",
                verbose_name="Страница вакансий",
            ),
        ),
    ]