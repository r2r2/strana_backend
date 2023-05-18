from __future__ import annotations

from itertools import groupby

from django.db.models import (
    F,
    Prefetch,
    QuerySet,
    Q,
    Case,
    When,
    Value,
    CharField,
    Count,
    IntegerField,
)
from django.db.models.functions import ExtractYear
from django.utils.timezone import now

from news.constants import ProgressMonth
from projects.models import Project


class NewsQuerySet(QuerySet):
    """
    Менеджер новостей
    """

    def active(self) -> NewsQuerySet:
        current_time = now()

        filter = (Q(start__lte=current_time) | Q(start__isnull=True)) & (
            Q(end__gte=current_time) | Q(end__isnull=True)
        )

        return self.filter(filter, published=True)

    def annotate_color(self) -> NewsQuerySet:

        prefetch = Prefetch("projects", Project.objects.annotate(color=F("city__color")))

        return self.prefetch_related(prefetch)

    def filter_city(self, city) -> NewsQuerySet:
        if city:
            return self.filter(projects__city=city).distinct()
        return self

    def annotate_year(self) -> NewsQuerySet:

        return self.annotate(year=ExtractYear("date"))

    def annotate_quarter(self) -> NewsQuerySet:
        quarter = Case(
            When(date__month__in=[1, 2, 3], then=Value("I", output_field=CharField())),
            When(date__month__in=[4, 5, 6], then=Value("II", output_field=CharField())),
            When(date__month__in=[7, 8, 9], then=Value("III", output_field=CharField())),
            When(date__month__in=[10, 11, 12], then=Value("IV", output_field=CharField())),
            default=None,
            output_field=CharField(),
        )
        return self.annotate(quarter=quarter)

    def annotate_month(self) -> NewsQuerySet:
        months = ProgressMonth.choices
        list_when_month = [
            When(date__month__in=[i + 1], then=Value(m[0], output_field=CharField()))
            for i, m in enumerate(months)
        ]
        month = Case(
            *list_when_month,
            default=None,
            output_field=CharField(),
        )

        list_when_month_number = [
            When(date__month__in=[i + 1], then=Value(i, output_field=IntegerField()))
            for i, m in enumerate(months)
        ]
        month_number = Case(
            *list_when_month_number,
            default=None,
            output_field=IntegerField(),
        )

        list_when_month_display = [
            When(date__month__in=[i + 1], then=Value(m[1], output_field=CharField()))
            for i, m in enumerate(months)
        ]
        month_display = Case(
            *list_when_month_display,
            default=None,
            output_field=CharField(),
        )
        return self.annotate(month=month, month_display=month_display, month_number=month_number)

    def filter_timeframed(self) -> NewsQuerySet:
        return self.filter(Q(start__lt=now()) | Q(start__isnull=True))

    def annotate_photo_count(self) -> "NewsQuerySet":

        photo_count = Count(
            "progressgallery",
            filter=(Q(progressgallery__image__isnull=False) & ~Q(progressgallery__image="")),
        )

        return self.annotate(photo_count=photo_count)

    def annotate_video_count(self) -> "NewsQuerySet":

        video_count = Count(
            "progressgallery",
            filter=(Q(progressgallery__video__isnull=False) & ~Q(progressgallery__video="")),
        )

        return self.annotate(video_count=video_count)

    def timeline_serialized(self):
        """
        :return: Список словарей с ключами month и days, хранящих целое число и список
        целых чисел соответственно.
        Пример:
        [
            {
                "year": 7,
                "month": [
                    1,2,3
                ]
            }
        ]
        """
        month_dict = {
            "january": "Январь",
            "february": "Февраль",
            "march": "Март",
            "april": "Апрель",
            "may": "Май",
            "june": "Июнь",
            "july": "Июль",
            "august": "Август",
            "september": "Сентябрь",
            "october": "Октябрь",
            "november": "Ноябрь",
            "december": "Декабрь",
        }
        timeline = list()
        dates = self.values_list("year", "month").order_by("-year", "-month_number")
        for year, month_dates in groupby(dates, lambda x: x[0]):  # простите
            month = []
            month_dates = [i[1] for i in month_dates]
            for i in ProgressMonth.choices:
                if i[0] in month_dates:
                    month.append(month_dict.get(i[0]))
            timeline.append({"year": year, "month": month})
        return timeline
