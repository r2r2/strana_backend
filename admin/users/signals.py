from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import CabinetUser, UserRole, Agency
from .utils import export_in_amo


@receiver(post_save, sender=CabinetUser)
def parse_client_type(
    sender, instance, created, **kwargs
):
    if update_fields := kwargs.get("update_fields"):
        if "type" in update_fields:
            role = UserRole.objects.filter(slug=instance.type).first()
            if role:
                instance.role = role
                instance.save()


@receiver(post_save, sender=CabinetUser)
def export_user_in_amo(
    sender, instance, created, raw, using, update_fields, *args, **kwargs
):
    try:
        export_in_amo(instanse_type="users", pk=instance.id)
    except Exception:
        pass


@receiver(post_save, sender=Agency)
def export_agency_in_amo(
    sender, instance, created, raw, using, update_fields, *args, **kwargs
):
    try:
        export_in_amo(instanse_type="agencies", pk=instance.id)
    except Exception:
        pass
