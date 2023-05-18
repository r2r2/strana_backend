from asyncio import gather
from typing import Any, Dict

from common.cor_handlers import AbstractCORHandler
from common.cor_states.wrappers import WrapperSpecsState


class SpecsFormResultDictHandler(AbstractCORHandler):
    def __init__(self, state: WrapperSpecsState):
        self.state: WrapperSpecsState = state

    async def handle(self):
        """Возвращает результат собраных спецификаций"""
        values: dict[str, Any] = dict(
            zip(
                self.state.aliases,
                await gather(*self.state.choices)
            )
        )

        return dict(ordering=self.state.ordering, specs=values)
