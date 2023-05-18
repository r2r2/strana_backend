from asyncio import Task
from copy import copy
from typing import Any, Optional, Type, Union, Callable

from common.email import EmailService
from config import site_config, aws_config
from src.properties.constants import PropertyTypes, PropertyStatuses
from src.properties.services import ImportPropertyService
from src.properties.repos import Property, PropertyRepo

from ..entities import BaseUserService
from ..repos import User
from ..types import UserEmail, UserInterestedRepo, UserORM, UserRepo


class CheckClientInterestService(BaseUserService):
    """
    Проверка избранного для уведомления клиента по почте при наличии изменений
    в объектах недвижимости (цена, статус, акции).
    """

    interest_property_changes_topic = "Новые акции и скидки для выбранных квартир"
    interest_property_status_changes_topic = "Изменение статуса выбранных квартир"
    interest_property_changes_template = "src/users/templates/interest_property_changes.html"
    interest_property_status_changes_template = "src/users/templates/interest_property_status_changes.html"
    favorites_link = "https://lk.{}/favorites?token={}"
    property_link = "https://{}/{}/flats/{}"

    def __init__(
        self,
        email_class: Type[UserEmail],
        interests_repo: Type[UserInterestedRepo],
        user_repo: Type[UserRepo],
        property_repo: Type[PropertyRepo],
        import_property_service: ImportPropertyService,
        token_creator: Callable[[int], dict[str, Any]],
        orm_class: Optional[Type[UserORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.user_repo: Type[UserRepo] = user_repo()
        self.property_repo: Type[PropertyRepo] = property_repo()
        self.email_class: Type[UserEmail] = email_class
        self.interests_repo: Type[UserInterestedRepo] = interests_repo()
        self.import_property_service: ImportPropertyService = import_property_service
        self.token_creator: Callable[[int], dict[str, Any]] = token_creator
        self.orm_class: Union[Type[UserORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self) -> None:
        users: list[User] = await self.user_repo.list(
            filters=dict(favorites__isnull=False),
            prefetch_fields=[
                "favorites__property",
                "favorites__property__project",
                "favorites__property__building",
                "favorites__property__floor"
            ]
        ).distinct()

        # словарь для хранения global_id объектов собственности, обновленных из портала (кеширование)
        updated_properies = {}

        for user in users:
            # словарь для сохранения данных по изменениям цены (скидка) и акциям в объектах собственности в избранном
            properties_data_with_offer_and_discount_info = {}
            # словарь для сохранения данных по изменениям статусов в объектах собственности в избранном
            properties_data_with_status_info = {}

            for user_interest in user.favorites:
                # проверяем изменения только для квартир
                if not user_interest.property.type or (user_interest.property.type == PropertyTypes.FLAT):
                    # флаг для фиксации наличия изменений в объекте избранного
                    property_changed = False

                    # обновляем объекты собственности клиента данными из БД портала
                    if user_interest.property.global_id not in updated_properies:
                        _, updated_property = await self.import_property_service(property=user_interest.property)
                        updated_properies[updated_property.global_id] = updated_property
                    else:
                        updated_property = updated_properies.get(user_interest.property.global_id)

                    # проверяем изменение цены (скидку) и сохраняем данные для отправки по почте клиенту
                    if price_difference := user_interest.interest_final_price - updated_property.final_price:
                        property_changed = True
                        if price_difference > 0:
                            await self._add_property_in_properties_data(
                                updated_property,
                                properties_data_with_offer_and_discount_info,
                                discount=self._get_price_info(price_difference),
                                special_offers=None,
                                only_free_flat=True,
                            )

                    # проверяем изменение акций и сохраняем данные для отправки по почте клиенту
                    if user_interest.interest_special_offers != updated_property.special_offers:
                        property_changed = True
                        if user_interest.interest_special_offers:
                            interest_special_offers = set(user_interest.interest_special_offers.split(", "))
                        else:
                            interest_special_offers = set()

                        if updated_property.special_offers:
                            property_special_offers = set(updated_property.special_offers.split(", "))
                        else:
                            property_special_offers = set()

                        added_special_offers = property_special_offers.difference(interest_special_offers)
                        if added_special_offers:
                            if property_data := properties_data_with_offer_and_discount_info.get(
                                    updated_property.global_id
                            ):
                                property_data.update(special_offers=list(added_special_offers))
                            else:
                                await self._add_property_in_properties_data(
                                    updated_property,
                                    properties_data_with_offer_and_discount_info,
                                    discount=None,
                                    special_offers=list(added_special_offers),
                                    only_free_flat=True,
                                )

                    # проверяем изменение статусов и сохраняем данные для отправки по почте клиенту
                    if user_interest.interest_status != updated_property.status.value:
                        property_changed = True
                        await self._add_property_in_properties_data(
                            updated_property,
                            properties_data_with_status_info,
                            status=updated_property.status,
                            similar_property_link=self.property_link.format(
                                site_config["main_site_host"],
                                updated_property.project.slug,
                                updated_property.similar_property_global_id
                            ),
                            special_offers=user_interest.property.special_offers.split(", ")
                            if user_interest.property.special_offers else None,
                        )

                    # обновляем сохраненные данные собственности в избранном при их изменении на портале
                    if property_changed:
                        await self.interests_repo.update(
                            user_interest,
                            {
                                "interest_final_price": updated_property.final_price,
                                "interest_status": updated_property.status.value,
                                "interest_special_offers": updated_property.special_offers,
                            }
                        )

            # проверяем наличие почты и подписки у клиента и отправляем письма по акциям и статусам (раздельно)
            if user.email and user.interested_sub:
                token = self._get_user_token(user)

                if properties_data_with_offer_and_discount_info:
                    await self._send_email_to_user(
                        recipient=user.email,
                        topic=self.interest_property_changes_topic,
                        template=self.interest_property_changes_template,
                        properties_data=list(properties_data_with_offer_and_discount_info.values())[:5],
                        favorites_link=self.favorites_link.format(site_config["main_site_host"], token),
                        site_link=site_config["main_site_host"],
                    )
                if properties_data_with_status_info:
                    await self._send_email_to_user(
                        recipient=user.email,
                        topic=self.interest_property_status_changes_topic,
                        template=self.interest_property_status_changes_template,
                        properties_data=list(properties_data_with_status_info.values())[:5],
                        favorites_link=self.favorites_link.format(site_config["main_site_host"], token),
                        site_link=site_config["main_site_host"],
                    )

    async def _add_property_in_properties_data(
        self,
        updated_property: Property,
        properties_data: dict[str, Any],
        only_free_flat: Optional[bool] = False,
        **params,
    ) -> None:
        """
        Сохраняем обновленные данные в словарь по объекту собственности для отправки клиенту на почту.
        """
        if only_free_flat and updated_property.status != PropertyStatuses.FREE:
            return None

        # (обход проблемы/бага tortoise)
        if updated_property.plan_png and isinstance(updated_property.plan_png, str):
            plan = f'https://storage.yandexcloud.net/{aws_config["storage_bucket_name"]}/{updated_property.plan_png}'
        elif updated_property.plan_png:
            plan = updated_property.plan_png.get("aws")
        elif isinstance(updated_property.plan, str):
            plan = f'https://storage.yandexcloud.net/{aws_config["storage_bucket_name"]}/{updated_property.plan}'
        else:
            plan = updated_property.plan.get("aws")

        properties_data[updated_property.global_id] = dict(
            global_id=updated_property.global_id,
            rooms=self._get_rooms_info(updated_property.rooms),
            area=self._get_area_info(updated_property.area),
            plan=plan,
            project=updated_property.project.name,
            building=updated_property.building.name,
            floor=updated_property.floor.number,
            total_floor=updated_property.total_floors,
            final_price=self._get_price_info(updated_property.final_price),
            property_link=self.property_link.format(
                site_config["main_site_host"],
                updated_property.project.slug,
                updated_property.global_id
            ),
        )
        properties_data[updated_property.global_id].update(params)

    async def _send_email_to_user(
        self,
        recipient: str,
        topic: str,
        template: str,
        **context
    ) -> Task:
        """
        Отправляем письмо на почту клиенту с информацией по изменениям
        объектов недвижимости в избранном.
        """

        email_options: dict[str, Any] = dict(
            topic=topic,
            template=template,
            recipients=[recipient],
            context=context,
        )
        email_service: EmailService = self.email_class(**email_options)

        return email_service.as_task()

    def _get_rooms_info(
        self,
        rooms: int,
    ) -> str:
        """
        Метод для корректного отображения инфо о комнатности объекта в письме.
        """

        if rooms == 0:
            return "Cтудия"
        if rooms in (1,5):
            return f"{rooms}-ком."
        else:
            return f"{rooms}x-ком."

    def _get_price_info(
        self,
        final_price: int,
    ) -> str:
        """
        Метод для корректного отображения цены объекта в письме (с отступами в тысячах).
        """

        return '{0:,}'.format(int(final_price)).replace(',', ' ')

    def _get_area_info(
        self,
        area: int,
    ) -> str:
        """
        Метод для корректного отображения площади объекта в письме.
        """

        return str(area).replace(".", ",")[:-1]

    def _get_user_token(self, user: User):
        token: str = self.token_creator(subject_type=user.type.value, subject=user.id)["token"]
        return token
