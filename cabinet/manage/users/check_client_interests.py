# pylint: disable=broad-except,redefined-builtin
from copy import copy
from typing import Any, Type

import structlog
from tortoise import Tortoise

from common import email, security
from common.utils import from_global_id
from config import tortoise_config
from src.notifications import repos as notification_repos
from src.notifications import services as notification_services
from src.properties import repos as properties_repos
from src.properties import services as property_services
from src.users import repos as users_repos
from src.users import services


class CheckClientInterestManage:
    """
    Проверка работы сервиса рассылки уведомлений для избранного клиентов.
    """

    def __init__(self) -> None:
        self.global_id_decoder = from_global_id
        self.property_repo: properties_repos.PropertyRepo = properties_repos.PropertyRepo()
        self.interests_repo: users_repos.InterestsRepo = users_repos.InterestsRepo()

        self.orm_class: Type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        self.orm_config.pop("generate_schemas", None)

        self.logger: structlog.BoundLogger = structlog.get_logger(__name__)

    async def __call__(self, *args, **kwargs) -> None:
        await self.orm_class.init(config=self.orm_config)

        user_id = args[0] if args else None
        try:
            user_id: int = int(user_id)
        except Exception:
            self.logger.error(f"Неверно передан {user_id=}")
            return

        result: bool = await self._update_client_interests(user_id=int(user_id))
        if result:
            await self._check_client_interests(user_id=user_id)

        await self.orm_class.close_connections()

    async def _update_client_interests(self, user_id: int) -> bool:
        """
        Обновление данных в избранном для проверки функционала.
        """

        users_interests: list[users_repos.UsersInterests] = await self.interests_repo.list(
            filters=dict(user_id=user_id),
        )
        if not users_interests:
            self.logger.error(f"У пользователя с {user_id=} нет квартир в избранном")
            return False

        for users_interest in users_interests:
            interest_data = {}
            if users_interest.interest_special_offers:
                interest_data.update(interest_special_offers='')
            elif users_interest.interest_final_price:
                interest_data.update(interest_final_price=users_interest.interest_final_price + 10000)

            interest_data.update(interest_status=2)

            await self.interests_repo.update(model=users_interest, data=interest_data)
            self.logger.info(
                f"У пользователя с {user_id=} обновлены данные в избранном {users_interest=} для проверки"
            )
        return True

    async def _check_client_interests(self, user_id: int) -> None:
        """
        Запуск сервиса рассылки уведомлений для избранного клиентов.
        """

        import_property_service: property_services.ImportPropertyService = \
            property_services.ImportPropertyServiceFactory.create(
                orm_class=Tortoise,
                orm_config=tortoise_config,
            )
        get_email_template_service: notification_services.GetEmailTemplateService = \
            notification_services.GetEmailTemplateService(
                email_template_repo=notification_repos.EmailTemplateRepo,
            )
        resources: dict[str, Any] = dict(
            email_class=email.EmailService,
            user_repo=users_repos.UserRepo,
            interests_repo=users_repos.InterestsRepo,
            property_repo=properties_repos.PropertyRepo,
            template_content=notification_repos.TemplateContentRepo,
            orm_class=Tortoise,
            orm_config=tortoise_config,
            import_property_service=import_property_service,
            get_email_template_service=get_email_template_service,
            token_creator=security.create_access_token,
        )
        check_client_interests: services.CheckClientInterestService = services.CheckClientInterestService(**resources)

        await check_client_interests(user_id=user_id, send_email_as_task=False)
        self.logger.info("Уведомления отправлены пользователям")
