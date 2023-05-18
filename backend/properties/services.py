from typing import Set, List
from django.db.models import Q, F
from buildings.models import Floor
from properties.constants import PropertyType


class WindowViewService:
    """
    Сервис для установки лотам вида из окна.
    Требуется минимальный этаж, максимальный этаж.

    Например, заданы этажи 1 - 9. На каждом этаже 10 квартир, тогда необходимо 10 видов из окна,
    для каждой квартиры упорядоченной по полю НОМЕР НА ЭТАЖЕ
    устанавливается соответствующий по порядку вид из окна.
    """

    def __init__(self, pk: int, min_floor: int, max_floor: int):
        from .models import WindowViewType, Property

        self.min_floor = min_floor
        self.max_floor = max_floor
        self.property = Property
        self._success = False
        self.errors = []
        self.obj = (
            WindowViewType.objects.select_related("building", "section")
            .prefetch_related("windowview_set", "miniplanpoint_set")
            .get(pk=pk)
        )
        self.floors = self.get_floors()
        self.flat_ids = self.get_flat_ids()

    def run(self):
        is_valid = self.validate()

        if is_valid:
            self.set_window_view()
        else:
            self._fail()

    def validate(self):
        is_valid = True
        flat_group_count = len(self.flat_ids)
        views_count = self.obj.windowview_set.count()
        mini_plan_count = self.obj.miniplanpoint_set.count()

        if views_count < flat_group_count:
            is_valid = False
            err = f"Количество видов ({views_count}) меньше количества групп квартир ({flat_group_count})"
            self.errors.append(err)

        if mini_plan_count < flat_group_count:
            is_valid = False
            err = f"Количество точек мини-плана ({mini_plan_count}) меньше количества групп квартир ({flat_group_count})"
            self.errors.append(err)

        return is_valid

    def set_window_view(self) -> None:
        window_view_qs = self.obj.windowview_set.order_by("order")
        mini_plan_point_qs = self.obj.miniplanpoint_set.order_by("order")

        for i, ids in enumerate(self.flat_ids):
            self.property.objects.filter(pk__in=ids).update(
                window_view=window_view_qs[i], mini_plan_point=mini_plan_point_qs[i]
            )

        self._set_success(True)

    def get_flat_ids(self) -> List[Set[int]]:
        flat_ids = [set() for _ in range(self.obj.windowview_set.count())]

        for floor in self.floors:
            flat_id_values = (
                floor.property_set.filter(type=PropertyType.FLAT)
                .order_by("number_on_floor")
                .values_list("pk", flat=True)
            )

            for index, _id in enumerate(flat_id_values):
                flat_ids[index].add(_id)
        flat_ids = list(filter(lambda x: len(x) >= 1, flat_ids))
        return flat_ids

    def get_floors(self):
        q = Q()
        if self.obj.section:
            q &= Q(section_id=self.obj.section_id)
        q &= Q(number__range=[self.min_floor, self.max_floor])

        return Floor.objects.filter(q, section__building=self.obj.building).prefetch_related(
            "property_set"
        )

    def _set_success(self, val: bool):
        self._success = val

    def is_successful(self):
        return self._success

    def _fail(self):
        self._set_success(False)

    @property
    def flats_count(self):
        flats_count = self.property.objects.filter(
            type=PropertyType.FLAT, floor__in=self.floors
        ).count()
        return flats_count


def update_layouts(layout_ids=None):
    from .models import Layout

    layout_qs = (
        Layout.objects.window_view_annotated()
        .annotate_max_discount()
        .annotate_min_price()
        .annotate_type()
        .annotate_property_stats_static()
        .annotate_mortgage_type()
        .annotate_min_mortgage()
        .annotate_min_rate()
    )

    if layout_ids:
        layout_qs = layout_qs.filter(id__in=layout_ids)

    layout_qs.update(
        window_view_id=F("window_view_a"),
        max_discount=F("max_discount_a"),
        min_price=F("min_price_a"),
        type=F("type_a"),
        planoplan=F("planoplan_a"),
        area=F("area_a"),
        rooms=F("rooms_a"),
        min_floor=F("min_floor_a"),
        max_floor=F("max_floor_a"),
        flat_count=F("flat_count_a"),
        has_view=F("has_view_a"),
        has_parking=F("has_parking_a"),
        has_action_parking=F("has_action_parking_a"),
        has_terrace=F("has_terrace_a"),
        has_high_ceiling=F("has_high_ceiling_a"),
        has_two_sides_windows=F("has_two_sides_windows_a"),
        has_panoramic_windows=F("has_panoramic_windows_a"),
        is_duplex=F("is_duplex_a"),
        installment=F("installment_a"),
        facing=F("facing_a"),
        frontage=F("frontage_a"),
        floor_plan=F("floor_plan_a"),
        floor_plan_width=F("floor_plan_width_a"),
        floor_plan_height=F("floor_plan_height_a"),
        preferential_mortgage4=F("preferential_mortgage4_a"),
        maternal_capital=F("maternal_capital_a"),
        hypo_popular=F("hypo_popular_a"),
        min_rate=F("min_rate_a"),
        design_gift=F("design_gift_a"),
        min_mortgage=F("min_mortgage_a"),
        flat_sold=F("flat_sold_a"),
        stores_count=F("stores_count_a"),
    )


def update_layout_min_mortgage(layout_id):
    from .models import Layout

    layout = (
        Layout.objects.filter(id=layout_id)
        .annotate_min_price()
        .annotate_mortgage_type()
        .annotate_min_mortgage()
    )
    layout.update(min_price=F("min_price_a"))
    layout.update(min_price=F("min_price_a"), min_mortgage=F("min_mortgage_a"))


def update_special_offers_activity():
    from .models import SpecialOffer

    offers = SpecialOffer.objects.filter(is_active=True).annotate_activity()
    offers.update(is_active=F("is_active_a"))


def update_properties_min_mortgage(project_id=None):
    from .models import Property

    q = Q(type=PropertyType.FLAT)
    if project_id:
        q &= Q(project_id=project_id)
    props = Property.objects.filter(q).annotate_mortgage_type().annotate_min_mortgage(20)
    props.update(hypo_min_mortgage=F("min_mortgage"))


def update_price_with_special_offers(project_id=None):
    from .models import Layout, Property

    q = Q()
    if project_id:
        q = Q(project_id=project_id)
    (
        Property.objects.filter(q)
        .exclude(original_price__isnull=True)
        .annotate_price_with_offer()
        .update(price=F("price_with_offer"))
    )
    Layout.objects.annotate_max_discount().update(max_discount=F("max_discount_a"))


def update_layouts_facing_by_property():
    from properties.models import Layout, Property

    layouts = Layout.objects.all()
    for layout in layouts:
        properties = Property.objects.filter(layout_id=layout.id).select_related('layout')
        property_facing = [props.facing for props in properties]
        if not layout.facing and any(property_facing):
            layout.facing = True
        elif layout.facing and not any(property_facing):
            layout.facing = False
    Layout.objects.bulk_update(layouts, ['facing'])
