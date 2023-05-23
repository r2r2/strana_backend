from uuid import uuid4

from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.fields import IntegerRangeField

from ..const import (AnotherTypeChoices, FormPayChoices, MeetingEndTypeChoices,
                     NextMeetingTypeChoices, PurchasePurposeChoices,
                     RoomsChoices)


class Meeting(models.Model):
    """Встреча."""

    id = models.UUIDField("ID", primary_key=True, default=uuid4)

    active = models.BooleanField("Активно", default=True)

    client = models.ForeignKey(
        "panel_manager.Client", models.CASCADE, blank=True, null=True, verbose_name="Клиент"
    )
    manager = models.ForeignKey(
        "panel_manager.Manager", models.CASCADE, blank=True, null=True, verbose_name="Менеджер"
    )
    project = models.ForeignKey(
        "projects.Project", models.SET_NULL, blank=True, null=True, verbose_name="Проект"
    )

    datetime_start = models.DateTimeField("Начало встречи", blank=True, null=True)
    datetime_end = models.DateTimeField("Конеч встречи", blank=True, null=True)

    agent_company = models.CharField("Агентство", max_length=200, blank=True)
    agent_fio = models.CharField("Агентство ФИО", max_length=300, blank=True)

    comment = models.TextField("Комментарий к встрече", blank=True)

    favorite_property = models.ManyToManyField(
        "properties.Property", blank=True, verbose_name="Избранные объекты"
    )
    purchase_purpose = models.IntegerField(
        "Цель покупки", choices=PurchasePurposeChoices.choices, blank=True, null=True
    )
    ad_question = models.TextField("Реклама", blank=True)
    stage_solution_question = models.TextField("Этап принятия решения", blank=True)
    agreed = models.TextField("О чем договорились на встрече", blank=True)
    adult_count = models.IntegerField("Количество взрослых", default=0)
    child_count = models.IntegerField("Количество детей", default=0)
    child_len = ArrayField(
        models.IntegerField(blank=True),
        size=10,
        verbose_name="Возраст детей",
        blank=True,
        null=True,
    )
    money = models.IntegerField("Бюджет", default=0)
    area = IntegerRangeField("Площадь", null=True, blank=True)
    floor = IntegerRangeField("Этаж", null=True, blank=True)
    form_pay = models.IntegerField(
        "Форма оплаты", choices=FormPayChoices.choices, blank=True, null=True
    )
    purchase_term = models.DateField(
        "Сроки покупки", null=True, default=None, blank=True
    )
    rooms = ArrayField(
        models.IntegerField("Комнатность", choices=RoomsChoices.choices, blank=True, null=True),
        size=100,
        verbose_name="Комнатность",
        blank=True,
        null=True,
    )
    another_type = ArrayField(
        models.IntegerField(
            "Дополнительные типы", choices=AnotherTypeChoices.choices, blank=True, null=True
        ),
        size=100,
        blank=True,
        null=True,
    )
    id_crm = models.CharField("ID в AmoCRM", max_length=200, blank=True, help_text="ID лида в AmoCRM")
    next_meeting_datetime = models.DateTimeField("Дата следующего контакта", blank=True, null=True)
    next_meeting_type = models.IntegerField(
        "Тип следующего контакта",
        choices=NextMeetingTypeChoices.choices,
        blank=True,
        null=True,
    )
    city = models.ForeignKey(
        "cities.City",
        verbose_name="Город",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    mortgage_approved = models.BooleanField("Ипотека одобрена?", default=False)
    date_reserved = models.DateTimeField("Дата резерва", blank=True, null=True)
    date_reserved_end = models.DateTimeField("Дата окончания резерва", blank=True, null=True)
    agency_deal = models.BooleanField("Сделка с Агентством?", default=False)
    meeting_end_type = models.IntegerField(
        "Тип окончания сделки", choices=MeetingEndTypeChoices.choices, blank=True, null=True
    )
    booked_property = models.ForeignKey(
        "properties.Property",
        models.SET_NULL,
        verbose_name="Забронированное помещение",
        blank=True,
        null=True,
        related_name="booked_property",
    )

    class Meta:
        verbose_name = "Встреча"
        verbose_name_plural = "Встречи"

    def __str__(self):
        return f"{self.client} {self.datetime_start}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_datetime_end = self.datetime_end

    def send_brochure(self):
        """Отправка брошуры"""
        from ..tasks import send_broshure

        if self.favorite_property.exists():
            send_broshure.delay(
                self.client.email, [str(i.id) for i in self.favorite_property.all()]
            )


class MeetingDetails(models.Model):
    """Выделенная модель для дополнительной информации о встрече.

    В дальнейшем предлагаю разделить на отдельные модели:
     - информацию об ипотеке
     - информацию об интересующем проекте/планировках/объектах собственности
     -
    """
    meeting = models.OneToOneField(
        Meeting, on_delete=models.CASCADE, verbose_name="встреча", related_name="details"
    )
    total_mortgage_amount = models.PositiveIntegerField(
        verbose_name="итоговая сумма ипотеки", default=0, blank=True
    )
    initial_payment = models.PositiveIntegerField(
        verbose_name="первоначальный взнос", default=0, blank=True
    )
    has_other_approvals = models.BooleanField(
        verbose_name="есть-ли одобрения в других банках", default=False, blank=True
    )

    class Meta:
        verbose_name = "блок ипотеки"
        verbose_name_plural = "блоки ипотеки"
        