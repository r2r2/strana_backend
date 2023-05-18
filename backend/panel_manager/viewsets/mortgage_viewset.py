import calendar
import collections as cl
import math
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django.core.cache import cache
from django.db.models import IntegerField, Max, Min, Prefetch, Value
from django.db.models.functions import Greatest, Least, Lower, Upper
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from mortgage.models import Bank, OfferPanel
from mortgage.serializers import BankSerializers, OfferPanelSerializers
from panel_manager.filters import PanelOfferFilterSet, BankFilter
from panel_manager.serializers.morgage import MortgagePanelLimits
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes


@extend_schema_view(
    list=extend_schema(
        summary="Банки",
        description="Список банков с агреггированной информацией по предложениям",
        parameters=[
            OpenApiParameter(
                name='price', type=OpenApiTypes.FLOAT, description='цена'
            ),
            OpenApiParameter(
                name='deposit', type=OpenApiTypes.INT, description='первый взнос'
            ),
            OpenApiParameter(
                name='term', type=OpenApiTypes.INT, description='срок, лет'
            )
        ]
    )
)
class PanelManagerBankViewSet(GenericViewSet):
    """Представления банков с ипотечными предложениями."""
    queryset = Bank.objects.all()
    serializer_class = BankSerializers
    filterset_class = BankFilter
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        queryset = super().get_queryset().annotate(payment=Value(None, output_field=IntegerField()))
        offer_qs = (
            OfferPanel.objects.filter(is_active=True)
            .select_related("program")
            .annotate(payment=Value(None, output_field=IntegerField()))
        )
        offer_qs = PanelOfferFilterSet(self.request.GET, offer_qs).qs
        if (
            "price" in self.request.GET
            and "deposit" in self.request.GET
            and "term" in self.request.GET
        ):
            try:
                price = int(self.request.GET["price"])
                deposit = Decimal(self.request.GET["deposit"])
                term = int(self.request.GET["term"])
                offer_qs = offer_qs.annotate_payment(price, deposit, term)
                queryset = queryset.annotate_payment(price, deposit, term, offer_qs)
            except (InvalidOperation, ValueError):
                pass
        offer_qs = PanelOfferFilterSet(self.request.GET, offer_qs).qs
        queryset = (
            queryset.prefetch_related(Prefetch("offerpanel_set", offer_qs))
            .filter(offerpanel__in=offer_qs)
            .annotate_min_rate()
            .annotate_max_term()
            .distinct()
            .order_by("order")
        )
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=("GET",))
    def specs(self, request):
        """Информация о параметрах запроса.

        Работает аналогично эндпоинту `offerpanel/specs/.
        """
        qs = Bank.objects.all()
        filter = BankFilter(request.GET, qs)
        return Response(filter.specs())

    @action(detail=False, methods=("GET",))
    def facets(self, request):
        filter = BankFilter(request.GET, self.queryset)
        return Response(filter.facets())


@extend_schema_view(
    list=extend_schema(
        summary="Ипотечные предложения",
        description="Список ипотечных предложений",
    )
)
class PanelManagerOfferViewSet(GenericViewSet):
    """
    ?price=2000000&deposit=30&term=10
    В фильтрах ипотечные программы имеют id вида UHJvZ3JhbVR5cGU6MQ
    Список программ и остальных параметров приходит с /api/panel/offer/specs/
    """

    serializer_class = OfferPanelSerializers
    filterset_class = PanelOfferFilterSet

    def get_queryset(self):
        offer_qs = OfferPanel.objects.filter(is_active=True).select_related("bank", "program")
        offer_qs = self.filter_queryset(offer_qs)
        try:
            price = int(self.request.GET.get("price", 10000000))
            deposit = Decimal(self.request.GET.get("deposit", 30))
            term = int(self.request.GET.get("term", 240))
            offer_qs = offer_qs.annotate_payment(price, deposit, term)
        except (InvalidOperation, ValueError):
            pass
        offer_order_filter = self.filterset_class(self.request.GET, offer_qs)
        offer_qs = offer_order_filter.qs
        return offer_qs

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=("GET",))
    def specs(self, request):
        offer_queryset = OfferPanel.objects.filter(is_active=True)
        filter = self.filterset_class(request.GET, offer_queryset)
        return Response(filter.specs())

    @action(detail=False, methods=("GET",))
    def facets(self, request):
        offer_queryset = OfferPanel.objects.filter(is_active=True)
        filter = self.filterset_class(request.GET, offer_queryset)
        return Response(filter.facets())

    @extend_schema(
        responses={200: MortgagePanelLimits}
    )
    @action(detail=False, methods=("GET", ))
    def limits(self, request):
        """Получение крайних значений по предложениям - используется для слайдеров и ползунков

        На данный момент поддерживается фильтрация по программе, типу, городу и банку.
        """
        qs = self.get_queryset()
        qs = qs.annotate(
            upper_rate=Greatest(Upper("rate"), Lower("rate")),
            lower_rate=Least(Upper("rate"), Lower("rate")),
            upper_term=Greatest(Lower("term"), Upper("term")),
            lower_term=Least(Upper("term"), Lower("term"))
        ).aggregate(
            max_rate=Max("upper_rate"), min_rate=Min("lower_rate"),
            max_term=Max("upper_term"), min_term=Min("lower_term")
        )
        serializer = MortgagePanelLimits(qs, read_only=True)
        return Response(serializer.data)

    def _get_payment_plan(self, request):
        """Расчет графика платежей"""
        deposit = self.request.GET.get("deposit")
        deposit = int(deposit) if deposit and deposit.isnumeric() else deposit
        deposit_sum = self.request.GET.get("deposit_sum")
        deposit_sum = int(deposit_sum) if deposit_sum and deposit_sum.isnumeric() else deposit_sum
        price = self.request.GET.get("price")
        price = int(price) if price and price.isnumeric() else price
        if deposit_sum:
            credit = price - deposit_sum
        elif deposit:
            credit = price * (100 - deposit) / 100
        else:
            credit = price
        term = self.request.GET.get("term")
        term = int(term) if term and term.isnumeric() else term
        rate = self.request.GET.get("rate")
        try:
            rate = float(rate)
        except Exception:
            rate = None
        date_now = now()
        specs = cl.OrderedDict()
        if credit and term and rate:
            month_rate = rate / 12 / 100  # Ежемесячная ставка
            count_month = term * 12  # Количество месяцев
            rate = (1 + month_rate) ** count_month
            month_pay = credit * month_rate * rate / (rate - 1)  # Ежемесячный платеж
            past_credit = credit

            data_per_month = []

            body = self.request.data
            # print(body_unicode)
            # body = {}
            # if body_unicode:
            #     body = json.loads(body_unicode)
            prepayment = body.get("prepayments", {})
            if prepayment:
                prepayment_new = {}
                for i in prepayment:
                    prepayment_new[f"{i['year']},{i['month']}"] = i
                prepayment = prepayment_new
            else:
                prepayment = {}

            i = 0  # счетчик месяцев

            while past_credit > 0:
                days = calendar.monthrange(date_now.year, date_now.month)[1]
                date_now += timedelta(days=days)
                specs[date_now.year] = specs.get(date_now.year, [])
                specs[date_now.year].append(date_now.month)

                if month_pay >= past_credit:  # Последний месяц платежа
                    percent_debt = round(past_credit * month_rate)  # Платеж процентная часть
                    credit_debt = past_credit
                    month_pay = credit_debt + percent_debt
                else:
                    percent_debt = round(past_credit * month_rate)  # Платеж процентная часть
                    credit_debt = round(month_pay - percent_debt)  # Платеж основная часть
                past_credit -= credit_debt  # Долг

                prepayment_month = prepayment.get(f"{date_now.year},{date_now.month}", None)
                if prepayment_month:
                    amount = int(prepayment_month["amount"])
                    if prepayment_month["type"] == "payment":
                        past_credit -= amount
                        # Перерасчет процента
                        rate = (1 + month_rate) ** (count_month - 1)
                        # Перерасчет ежемесячного платежа
                        month_pay = past_credit * month_rate * rate / (rate - 1)
                        print(date_now.month, rate, month_pay, count_month)
                        data_per_month.append(
                            {
                                "type": "prepayment",
                                "type_pay": "payment",
                                "number_pay_month": i + 1,
                                "past_credit": past_credit,
                                "date": date_now,  # Дата платежа
                                "month": date_now.month,
                                "year": date_now.year,
                                "amount": amount,
                            }
                        )
                    elif prepayment_month["type"] == "term":
                        past_credit -= amount
                        # Перерасчет количества месяцев
                        count_month = math.ceil(
                            math.log(
                                (month_pay / (month_pay - (month_rate * past_credit))),
                                1 + month_rate,
                            )
                        )
                        data_per_month.append(
                            {
                                "type": "prepayment",
                                "type_pay": "term",
                                "number_pay_month": i + 1,
                                "past_credit": past_credit,
                                "date": date_now,  # Дата платежа
                                "month": date_now.month,
                                "year": date_now.year,
                                "amount": amount,
                            }
                        )

                data_per_month.append(
                    {
                        "type": "line",
                        "number_pay_month": i + 1,
                        "percent": percent_debt,
                        "credit": credit_debt,
                        "month_pay": round(month_pay),
                        "past_credit": past_credit,
                        "date": date_now,  # Дата платежа
                        "month": date_now.month,
                        "year": date_now.year,
                    }
                )
                i += 1
                count_month -= 1
            specs = [{"value": key, "months": values} for key, values in specs.items()]
            return data_per_month, specs
        return {}, None

    @action(methods=["get", "post"], detail=False)
    def payment_plan(self, request, *args, **kwargs):
        """График платежей
        ?price=2000000&deposit=30&term=10&rate=7
        """
        plan, _ = self._get_payment_plan(request)
        return Response(data=plan)

    @action(methods=["get", "post"], detail=False)
    def payment_plan_specs(self, request, *args, **kwargs):
        """Спеки для график платежей
        ?price=2000000&deposit=30&term=10&rate=7
        """
        _, specs = self._get_payment_plan(request)
        return Response(data=specs)

    @action(methods=["get", "post"], detail=False)
    def pdf_payment_plan(self, request, *args, **kwargs):
        if request.method == "POST":
            body = request.data
            if body:
                ref_id = uuid4()
                cache.set(f"pdf_form_{ref_id}", body, 120)
                return Response(data={"ref_id": ref_id})
            return Response(data={"ref_id": None})
        ref_id = self.request.GET.get("ref_id", None)
        if ref_id:
            body = cache.get(f"pdf_form_{ref_id}", {})
            return Response(data=body)
        return Response()
