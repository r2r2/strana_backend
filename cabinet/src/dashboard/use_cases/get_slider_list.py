class GetSliderList:
    pass

from typing import Any, Type, Optional, Union
from ..entities import BaseSliderRepo, BaseDashboardCase
from ..exceptions import SlideNotFoundError
from ..repos import Slider, SliderRepo
from tortoise.queryset import QuerySet
from ..constants import DeviceType


class GetSliderListCase(BaseDashboardCase):
    """
    Получение взаимодействий.
    """

    def __init__(self, slider_repo: Type[SliderRepo]) -> None:
        self.slider_repo: SliderRepo = slider_repo()

    async def __call__(
        self,
    ) -> list[Slider]:
        active_filters: dict[str, bool] = dict(
            is_active=True
        )
        sliders: list[Slider] = await self.slider_repo.list(
            filters=active_filters
        )
        return sliders