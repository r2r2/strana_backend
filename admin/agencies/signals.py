from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Agency
from .utils import export_in_amo


@receiver(post_save, sender=Agency)
def export_agency_in_amo(
    sender, instance, created, raw, using, update_fields, *args, **kwargs
):
    try:
        export_in_amo(instanse_type="agencies", pk=instance.id)
    except Exception:
        pass
