from __future__ import annotations
from django.db.models import F, Q, QuerySet, Min, Max, ExpressionWrapper, Case, When, Value
from django.db.models.fields import FloatField, IntegerField
from django.db.models.functions import Lower, Upper, Least, Greatest, Cast
from common.models import Power


class BankQuerySet(QuerySet):
    """
    Менеджер банков
    """

    def annotate_min_rate(self, offers=None) -> BankQuerySet:

        filter_expression = Q(offerpanel__is_active=True)
        if offers is not None:
            filter_expression = Q(offerpanel__id__in=offers)

        min_rate = Min(Least(Upper("offerpanel__rate"), Lower("offerpanel__rate")), filter=filter_expression)
        subs_min_rate = Min(
            Least(Upper("offerpanel__subs_rate"), Lower("offerpanel__subs_rate")), filter=filter_expression
        )

        return self.annotate(min_rate=min_rate, min_subs_rate=subs_min_rate)

    def annotate_max_term(self, offers=None) -> BankQuerySet:

        filter_expression = Q(offerpanel__is_active=True)
        if offers is not None:
            filter_expression = Q(offerpanel__id__in=offers)

        max_term = Max(
            Greatest(Upper("offerpanel__term"), Lower("offerpanel__term")), filter=filter_expression
        )
        subs_max_term = Max(
            Greatest(Upper("offerpanel__subs_term"), Lower("offerpanel__subs_term")), filter=filter_expression
        )

        return self.annotate(max_term=max_term, max_subs_term=subs_max_term)

    def annotate_payment(self, price, deposit, term, offers=None) -> BankQuerySet:
        price -= price * deposit / 100

        filter_expression = Q(offerpanel__is_active=True)
        if offers is not None:
            filter_expression = Q(offerpanel__id__in=offers)

        i = Min(
            Least(Lower("offerpanel__rate"), Upper("offerpanel__rate")) / 1200,
            output_field=FloatField(),
            filter=filter_expression,
        )
        s = Min(
            Least(Lower("offerpanel__subs_rate"), Upper("offerpanel__subs_rate")) / 1200,
            output_field=FloatField(),
            filter=filter_expression,
        )

        payment = ExpressionWrapper(
            price * F("i") * Power(F("i") + 1, term * 12) / (Power(F("i") + 1, term * 12) - 1),
            output_field=IntegerField(),
        )
        subs_payment = ExpressionWrapper(
            price * F("s") * Power(F("s") + 1, term * 12) / (Power(F("s") + 1, term * 12) - 1),
            output_field=IntegerField(),
        )

        return self.annotate(i=i, s=s, payment=payment, subs_payment=subs_payment)


class OfferQuerySet(QuerySet):
    """
    Менеджер предложений по ипотеке
    """

    def annotate_payment(self, price, deposit, term) -> OfferQuerySet:
        price -= price * deposit / 100

        i = Least(Upper("rate"), Lower("rate"), output_field=FloatField()) / 1200
        s = Least(Upper("subs_rate"), Lower("subs_rate"), output_field=FloatField()) / 1200

        payment = ExpressionWrapper(
            price * F("i") * Power(F("i") + 1, term * 12) / (Power(F("i") + 1, term * 12) - 1),
            output_field=IntegerField(),
        )

        st = Least(Upper("subs_term"), Lower("subs_term"), output_field=FloatField())

        subs_payment_case = Case(
            When(
                Q(st__gt=0),
                then=ExpressionWrapper(
                    price
                    * F("s")
                    * Power(F("s") + 1, term * 12)
                    / (Power(F("s") + 1, term * 12) - 1),
                    output_field=IntegerField(),
                ),
            ),
            output_field=IntegerField(),
            default=None,
        )

        return self.annotate(i=i, s=s, st=st, payment=payment, subs_payment=subs_payment_case)

    def annotate_filter_price(self, price: int, deposit: int) -> OfferQuerySet:

        price_f = ExpressionWrapper(
            Cast(price - deposit, output_field=IntegerField()), output_field=IntegerField()
        )

        return self.annotate(price_f=price_f)
