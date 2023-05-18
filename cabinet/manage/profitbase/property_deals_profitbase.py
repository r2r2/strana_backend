# pylint: disable=broad-except,redefined-builtin
import structlog
import ujson
from common.profitbase import ProfitBase
from common import utils


class PropertyDealsPropertyProfitbase:
    """
    Список сделок недвидимости
    """
    def __init__(self) -> None:
        self.global_id_decoder = utils.from_global_id
        self.profitbase_class = ProfitBase
        self.logger = structlog.getLogger(__name__)

    async def __call__(self, property_id: str) -> None:
        """
        Profitbase property deals
        """
        _, property_id = self.global_id_decoder(global_id=property_id)
        async with await self.profitbase_class() as profitbase:
            data: dict[str, bool] = await profitbase.deals_list(property_id=property_id)
        self.logger.info(f"Property deals: {ujson.dumps(data)}")
