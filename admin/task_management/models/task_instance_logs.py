from common.loggers.models import AbstractLog
from django.db import models


class TaskInstanceLog(AbstractLog):
    task_instance = models.ForeignKey("task_management.TaskInstance", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.use_case} – {self.content}" if self.use_case and self.content else self

    class Meta:
        db_table = "task_management_logs"
        verbose_name = "Лог: "
        verbose_name_plural = "Логи задач"
