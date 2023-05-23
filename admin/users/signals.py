from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import CabinetUser
from agencies.utils import export_in_amo


@receiver(post_save, sender=CabinetUser)
def export_user_in_amo(
    sender, instance, created, raw, using, update_fields, *args, **kwargs
):
    try:
        export_in_amo(instanse_type="users", pk=instance.id)
    except Exception:
        pass
