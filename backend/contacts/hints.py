from django.db.models import Prefetch
from graphene_django_optimizer import query
from .models import Subdivision


def office_resolve_subdivision_set_hint(info) -> Prefetch:
    queryset = query(Subdivision.objects.filter(active=True), info)
    return Prefetch("subdivision_set", queryset)
