from common import mixins


class WidthType(mixins.Choices):
    MIN_WIDTH: int = 1, "Минимальная ширина"
    MIDDLE_WIDTH: int = 2, "Средняя ширина"
    MAX_WIDTH: int = 3, "Максимальная ширина"

    def __int__(self):
        return self.value
