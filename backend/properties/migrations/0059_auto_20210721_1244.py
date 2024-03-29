# Generated by Django 3.0.10 on 2021-07-21 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("properties", "0058_auto_20210713_1101")]

    operations = [
        migrations.AddField(
            model_name="property",
            name="preferential_mortgage_4",
            field=models.BooleanField(
                db_index=True, default=False, verbose_name="Льготная ипотека 4.95%"
            ),
        ),
        migrations.AlterField(
            model_name="feature",
            name="kind",
            field=models.CharField(
                choices=[
                    ("facing", "Отделка"),
                    ("has_parking", "Паркинг"),
                    ("has_action_parking", "Паркинг по спец. цене"),
                    ("has_terrace", "Терраса"),
                    ("has_view", "Видовые"),
                    ("has_panoramic_windows", "Панорамные окна"),
                    ("has_two_sides_windows", "Окна на 2 стороны"),
                    ("is_duplex", "Двухуровневая"),
                    ("has_high_ceiling", "Высокий потолок"),
                    ("installment", "Рассрочка"),
                    ("frontage", "Палисадник"),
                    ("preferential_mortgage", "Льготная ипотека"),
                    ("preferential_mortgage_4", "Льготная ипотека 4.95%"),
                    ("has_tenant", "С арендатором"),
                    ("action", "Акция"),
                    ("favorable_rate", "Выгодная ставка"),
                    ("completed", "Завершенная"),
                    ("corner_windows", "Угловые окна"),
                ],
                default="facing",
                max_length=48,
                verbose_name="Тип",
            ),
        ),
    ]
