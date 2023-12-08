from common import mixins
from enum import StrEnum


class WidthType(mixins.Choices):
    MIN_WIDTH: int = 1, "Минимальная ширина"
    MIDDLE_WIDTH: int = 2, "Средняя ширина"
    MAX_WIDTH: int = 3, "Максимальная ширина"

    def __int__(self):
        return self.value
    
class DeviceType(StrEnum):
    desktop_media: str = "desktop_media"
    tablet_media: str = "tablet_media"
    mobile_media: str = "mobile_media"
