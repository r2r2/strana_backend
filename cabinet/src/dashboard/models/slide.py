from datetime import datetime
from typing import Optional, Any, Union

from src.dashboard.entities import BaseSliderModel

class ResponseGetSlider(BaseSliderModel):
    """
    Модель ответа по слайдеру.
    """
    id: int
    title: str
    subtitle: str
    desktop_media: Optional[Any]
    tablet_media: Optional[Any]
    mobile_media: Optional[Any]
    
    class Config:
        orm_mode = True