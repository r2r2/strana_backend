from django.db.models import Subquery, Q, OuterRef, F
from django.db.models.functions import Upper, Least, Lower
from .models import Offer, MortgagePage, MortgageAdvantage


def calculate_mortgage_page_min_value() -> None:
    min_value_page = Subquery(
        Offer.objects.filter(Q(is_active=True) & Q(city__site=OuterRef("site")))
        .annotate(min_rate=Least(Upper("rate"), Lower("rate")))
        .order_by("min_rate")
        .values("min_rate")[:1]
    )
    pages = MortgagePage.objects.annotate(min_value_a=min_value_page)
    pages.update(min_value=F("min_value_a"))
    advantages = MortgageAdvantage.objects.filter(page__isnull=False).select_related("page")
    for advantage in advantages:
        setattr(advantage, "min_value", advantage.page.min_value)
    MortgageAdvantage.objects.bulk_update(advantages, ["min_value"])