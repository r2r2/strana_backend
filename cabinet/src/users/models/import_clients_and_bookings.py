from src.users.entities import BaseUserModel


class RequestImportClientsAndBookingsModel(BaseUserModel):
    """
    Модель запроса запуска сервиса импорта клиентов (и сделок) для брокера из админки.
    """
    broker_id: int
