# Generated by Django 3.0.8 on 2020-09-15 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0005_auto_20200723_1422"),
    ]

    operations = [
        migrations.AddField(
            model_name="property",
            name="has_high_ceiling",
            field=models.BooleanField(default=False, verbose_name="Высокий потолок"),
        ),
        migrations.AddField(
            model_name="property",
            name="has_panoramic_windows",
            field=models.BooleanField(default=False, verbose_name="Панорамные окна"),
        ),
        migrations.AddField(
            model_name="property",
            name="has_parking",
            field=models.BooleanField(default=False, verbose_name="Парковка"),
        ),
        migrations.AddField(
            model_name="property",
            name="has_terrace",
            field=models.BooleanField(default=False, verbose_name="Терраса"),
        ),
        migrations.AddField(
            model_name="property",
            name="has_two_sides_windows",
            field=models.BooleanField(default=False, verbose_name="Окна на 2 стороны"),
        ),
        migrations.AddField(
            model_name="property",
            name="is_duplex",
            field=models.BooleanField(default=False, verbose_name="Двухуровневая"),
        ),
        migrations.AddField(
            model_name="property",
            name="stores_count",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="Количество кладовых"
            ),
        ),
        migrations.AddField(
            model_name="property",
            name="wardrobes_count",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="Количество гардеробных"
            ),
        ),
    ]