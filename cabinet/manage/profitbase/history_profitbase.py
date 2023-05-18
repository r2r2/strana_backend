# pylint: disable=broad-except,redefined-builtin
import structlog
import ujson
from typing import Optional
from common import utils
from common.profitbase import ProfitBase


class HistoryPropertyProfitbase:
    """
    Мануальная проверка квартиры в profitbase
    """
    def __init__(self) -> None:
        self.global_id_decoder = utils.from_global_id
        self.profitbase_class = ProfitBase
        self.logger = structlog.getLogger(__name__)

    async def __call__(self, property_id: str) -> None:
        """
        Profitbase check property
        """
        _, property_id = self.global_id_decoder(global_id=property_id)
        async with await self.profitbase_class() as profitbase:
            if not profitbase.errors:
                property_history: Optional[list] = await profitbase.get_property_history(
                    property_id=int(property_id),
                )
                self.logger.info(f"Property history: {ujson.dumps(property_history)}")
            else:
                self.logger.info(f"Profitbase errors: {profitbase.errors}")
