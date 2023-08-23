from django.db import models

from ..utils import send_email_to_agent


class EventParticipantStatus(models.TextChoices):
    """
    Статус участника мероприятия.
    """
    RECORDED: tuple[str] = "recorded", "Записан"
    REFUSED: tuple[str] = "refused", "Отказался"


class EventParticipant(models.Model):
    """
    Участник мероприятия.
    """

    __original_status = None

    fio = models.TextField(verbose_name="ФИО агента участника")
    phone = models.CharField(verbose_name="Номер телефона агента участника", max_length=20)
    agent = models.ForeignKey(
        "users.CabinetUser",
        models.CASCADE,
        related_name="participants",
        verbose_name="Агент участник"
    )
    status: str = models.CharField(
        verbose_name="Статус агента участника",
        max_length=20,
        choices=EventParticipantStatus.choices,
    )
    event = models.ForeignKey(
        "events.Event",
        models.CASCADE,
        related_name="participants",
        verbose_name="Мероприятие"
    )

    def __str__(self):
        return f"{self.fio}, {self.phone}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_status = self.status

    def save(self, *args, **kwargs):
        if self.agent:
            self.fio = f"{self.agent.surname} {self.agent.name} {self.agent.patronymic}"
            self.phone = self.agent.phone
        if self.agent:
            self.fio = f"{self.agent.surname} {self.agent.name} {self.agent.patronymic}"
            self.phone = self.agent.phone
        if self.__original_status and self.status != self.__original_status:
            try:
                send_email_to_agent(
                    agent_id=self.agent.id,
                    event_id=self.event.id,
                    agent_status=self.status,
                )
            except Exception:
                pass
        super().save()
        self.__original_status = self.status

    class Meta:
        managed = False
        db_table = "event_event_participant"
        verbose_name = "Участник мероприятия"
        verbose_name_plural = "Участники мероприятия"
