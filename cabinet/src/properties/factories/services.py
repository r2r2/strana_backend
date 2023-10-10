from src.properties.services import CheckProfitbasePropertyService
from common import profitbase, utils


class CheckProfitbasePropertyServiceFactory:
    @staticmethod
    def create() -> CheckProfitbasePropertyService:
        return CheckProfitbasePropertyService(
            global_id_decoder=utils.from_global_id,
            profitbase_class=profitbase.ProfitBase,
        )
