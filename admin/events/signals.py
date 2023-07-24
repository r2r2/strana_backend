from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from .models import EventParticipant, EventParticipantStatus
from .utils import send_email_to_agent


@receiver(post_save, sender=EventParticipant)
def send_email_to_agent_on_record(
    sender, instance, created, raw, using, update_fields, *args, **kwargs
):
    if created and instance.status == EventParticipantStatus.RECORDED:
        try:
            send_email_to_agent(
                agent_id=instance.agent.id,
                event_id=instance.event.id,
                agent_status=EventParticipantStatus.RECORDED,
            )
        except Exception:
            pass


@receiver(pre_delete, sender=EventParticipant)
def send_email_to_agent_on_refused(
    sender, instance, using, *args, **kwargs
):
    try:
        send_email_to_agent(
            agent_id=instance.agent.id,
            event_id=instance.event.id,
            agent_status=EventParticipantStatus.REFUSED,
        )
    except Exception:
        pass
