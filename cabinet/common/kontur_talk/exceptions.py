class BaseKonturTalkRequestException(Exception):
    """
    Базовая ошибка запроса в Kontur Talk
    """

    message: str
    status: int
    reason: str