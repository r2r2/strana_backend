from django.utils.timezone import now
from django.db.models import Case, When, F, BooleanField
from common.models import ActiveQuerySet


class MainPageSlideQuerySet(ActiveQuerySet):
    def annotate_activity(self):

        is_active = Case(
            When(end_date__isnull=False, end_date__lt=now(), then=False),
            default=F("is_active"),
            output_field=BooleanField(),
        )

        return self.annotate(is_active_a=is_active)
