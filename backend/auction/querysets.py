from django.utils.timezone import now
from django.db.models import Q, F, QuerySet, Case, When, BooleanField, IntegerField


class AuctionQuerySet(QuerySet):
    def not_finished(self):
        return self.filter(end__gte=now())

    def filter_active(self):
        return self.filter(is_active=True)

    def annotate_is_current(self):

        is_current = Case(
            When(Q(start__lte=now()) & Q(end__gte=now()), then=True),
            default=False,
            output_field=BooleanField(),
        )

        return self.annotate(is_current=is_current)

    def annotate_current_price(self):
        current_price = Case(
            When(bet_count__gt=0, then=F("start_price") + F("step") * F("bet_count")),
            default=F("start_price"),
            output_field=IntegerField(),
        )
        return self.annotate(current_price=current_price)


class NotificationQuerySet(QuerySet):
    def timeframed(self):
        return self.filter((Q(auction__start__lte=now())) & (Q(auction__end__gte=now())))
