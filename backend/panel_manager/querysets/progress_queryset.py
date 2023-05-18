from itertools import groupby

from django.db.models import QuerySet, Count, Q


class ProgressQuerySet(QuerySet):
    """
    Менеджер ходов строительства
    """

    def active(self) -> "ProgressQuerySet":
        return self.filter(active=True)

    def annotate_photo_count(self) -> "ProgressQuerySet":

        photo_count = Count(
            "progressgallery",
            filter=(Q(progressgallery__image__isnull=False) & ~Q(progressgallery__image="")),
        )

        return self.annotate(photo_count=photo_count)

    def annotate_video_count(self) -> "ProgressQuerySet":

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
        dates = self.values_list("year", "month").order_by("year", "-month")
        for year, month_dates in groupby(dates, lambda x: x[0]):  # простите
            month = []
            month_dates = [i[1] for i in month_dates]
            # for i in ProgressMonth.choices:
            #     if i[0] in month_dates:
            #         month.append(month_dict.get(i[0]))
            timeline.append({"year": year, "month": month})
        return timeline
