from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from .models import Booking
from agencies.utils import export_in_amo


@receiver(post_save, sender=Booking)
def free_property_on_inactive(
    sender, instance, created, raw, using, update_fields, *args, **kwargs
):
    if (not instance.property and created) or instance.active:
        return
    # free_property(sender, instance, using, *args, **kwargs)


@receiver(pre_delete, sender=Booking)
def free_property(sender, instance, using, *args, **kwargs):
    if not instance.property:
        return
    flat = instance.property
    instance.property = None
    instance.project = None
    instance.building = None
    instance.save()
    if flat.status == 2:
        flat.status = 0
        flat.save()


@receiver(post_save, sender=Booking)
def export_booking_in_amo(
    sender, instance, created, raw, using, update_fields, *args, **kwargs
):
    try:
        export_in_amo(instanse_type="booking", pk=instance.id)
    except Exception:
        pass
