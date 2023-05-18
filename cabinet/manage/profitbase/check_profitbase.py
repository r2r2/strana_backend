# pylint: disable=broad-except,redefined-builtin
import structlog
import ujson
from typing import Optional, Any
from common import utils
from common.profitbase import ProfitBase
from src.properties.constants import PropertyStatuses


class CheckPropertyProfitbase:
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
            if profitbase.errors:
                key_ok: bool = False
                mapped_status: int = PropertyStatuses.FREE
            else:
                property_data: Optional[dict[str, Any]] = await profitbase.get_property(
                    property_id=int(property_id), full=True,
                )
                self.logger.info(f"Property data: {ujson.dumps(property_data)}")
                if not property_data:
                    key_ok: bool = True
                    mapped_status: int = PropertyStatuses.FREE
                else:
                    key_ok: bool = property_data["status"] == profitbase.status_success
                    mapped_status: int = getattr(
                        PropertyStatuses,
                        profitbase.status_mapping.get(property_data["status"], "BOOKED"),
                    )
        self.logger.info(f"Check profitbase: mapped_status={mapped_status}, key_ok={key_ok}")
