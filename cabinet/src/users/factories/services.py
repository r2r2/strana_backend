from common.amocrm import amocrm
from config import amocrm_config
from src.users.services import CheckPinningStatusServiceV2, CheckPinningStatusService
from src.users import repos as users_repos


class CheckPinningStatusServiceFactory:
    @staticmethod
    def create_v1():
        return CheckPinningStatusService(
            amocrm_class=amocrm.AmoCRM,
            user_repo=users_repos.UserRepo,
            check_pinning_repo=users_repos.PinningStatusRepo,
            user_pinning_repo=users_repos.UserPinningStatusRepo,
            amocrm_config=amocrm_config,
        )

    @staticmethod
    def create():
        return CheckPinningStatusServiceV2(
            user_repo=users_repos.UserRepo,
            check_pinning_repo=users_repos.PinningStatusRepo,
            user_pinning_repo=users_repos.UserPinningStatusRepo,
        )
