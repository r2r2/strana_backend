# pylint: disable=broad-except,redefined-builtin
import structlog
import ujson
from common.profitbase import ProfitBase, ProfitbaseStatuses
from common import utils


class UnbookingPropertyProfitbase:
    """
    Мануальное разбронирование квартиры в profitbase
    """
    def __init__(self) -> None:
        self.global_id_decoder = utils.from_global_id
        self.profitbase_class = ProfitBase
        self.logger = structlog.getLogger(__name__)

    async def __call__(self, property_id: str) -> None:
        """
        Profitbase unbooking
        """
        _, property_id = self.global_id_decoder(global_id=property_id)
        async with await self.profitbase_class() as profitbase:
            data: dict[str, bool] = await profitbase.change_property_status(
                property_id=property_id,
                status=ProfitbaseStatuses.AVAILABLE,
            )
        self.logger.info(f"Unbooking profitbase: {ujson.dumps(data)}")
