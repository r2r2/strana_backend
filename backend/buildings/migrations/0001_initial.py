# Generated by Django 3.0.7 on 2020-06-08 15:36

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [("projects", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Building",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=50, verbose_name="Название")),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("RESIDENTIAL", "Жилое"),
                            ("APARTMENT", "Апартаменты"),
                            ("PARKING", "Паркинг"),
                            ("OFFICE", "Коммерческое"),
                        ],
                        db_index=True,
                        default="RESIDENTIAL",
                        max_length=32,
                        verbose_name="Тип строения",
                    ),
                ),
                (
                    "number",
                    models.CharField(
                        blank=True, db_index=True, max_length=50, verbose_name="Номер"
                    ),
                ),
                (
                    "building_state",
                    models.CharField(
                        choices=[
                            ("unfinished", "Cтроится"),
                            ("built", "Построен, но не сдан"),
                            ("ready", "Построен и сдан"),
                            ("hand_over", "Сдан в эксплуатацию"),
                        ],
                        max_length=20,
                        verbose_name="Состояние",
                    ),
                ),
                (
                    "built_year",
                    models.PositiveIntegerField(
                        blank=True,
                        db_index=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1900),
                            django.core.validators.MaxValueValidator(2100),
                        ],
                        verbose_name="Год сдачи",
                        help_text='Высчитывается автоматически из поля "Дата окончания строительства"',
                    ),
                ),
                (
                    "ready_quarter",
                    models.PositiveIntegerField(
                        blank=True,
                        db_index=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(4),
                        ],
                        verbose_name="Квартал сдачи",
                        help_text='Высчитывается автоматически из поля "Дата окончания строительства"',
                    ),
                ),
                (
                    "building_phase",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Очередь строительства"
                    ),
                ),
                (
                    "building_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("panel", "Панельный"),
                            ("monolithic", "Монолитный"),
                            ("brick", "Кирпичный"),
                            ("brick_monolithic", "Кирпично-монолитный"),
                        ],
                        max_length=20,
                        verbose_name="Тип",
                    ),
                ),
                (
                    "ceiling_height",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=4,
                        null=True,
                        verbose_name="Высота потолков",
                    ),
                ),
                (
                    "passenger_lifts_count",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Количество пассажирских лифтов"
                    ),
                ),
                (
                    "cargo_lifts_count",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Количество грузовых лифтов"
                    ),
                ),
                (
                    "cian_id",
                    models.PositiveIntegerField(blank=True, null=True, verbose_name="ID в cian"),
                ),
                (
                    "yandex_id",
                    models.PositiveIntegerField(blank=True, null=True, verbose_name="ID в Yandex"),
                ),
                (
                    "changed",
                    models.DateTimeField(auto_now=True, db_index=True, verbose_name="Изменено"),
                ),
                (
                    "hash",
                    models.BinaryField(blank=True, max_length=20, null=True, verbose_name="Хэш"),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="projects.Project",
                        verbose_name="Проект",
                    ),
                ),
            ],
            options={
                "verbose_name": "Корпус",
                "verbose_name_plural": "Корпуса",
                "ordering": ("name",),
                "unique_together": {("project", "name")},
            },
        ),
        migrations.CreateModel(
            name="Section",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=50, verbose_name="Название")),
                ("number", models.PositiveIntegerField(db_index=True, verbose_name="Номер")),
                (
                    "changed",
                    models.DateTimeField(auto_now=True, db_index=True, verbose_name="Изменено"),
                ),
                (
                    "building",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="buildings.Building",
                        verbose_name="Корпус",
                    ),
                ),
            ],
            options={
                "verbose_name": "Секция",
                "verbose_name_plural": "Секции",
                "ordering": ("number",),
                "unique_together": {("building", "number")},
            },
        ),
        migrations.CreateModel(
            name="Floor",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("number", models.IntegerField(db_index=True, verbose_name="Номер")),
                (
                    "changed",
                    models.DateTimeField(auto_now=True, db_index=True, verbose_name="Изменено"),
                ),
                (
                    "section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="buildings.Section",
                        verbose_name="Секция",
                    ),
                ),
            ],
            options={
                "verbose_name": "Этаж",
                "verbose_name_plural": "Этажи",
                "ordering": ("number",),
                "unique_together": {("section", "number")},
            },
        ),
    ]