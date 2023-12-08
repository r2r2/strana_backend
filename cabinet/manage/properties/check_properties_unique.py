# pylint: disable=broad-except,redefined-builtin
import structlog
import binascii
from copy import copy
from typing import Any, Type
from pydantic import ValidationError

from config import tortoise_config
from src.properties import repos as properties_repos
from src.booking import repos as bookings_repos
from src.users import repos as users_repos
from tortoise import Tortoise

from common.utils import from_global_id
from ..models import PropertyIdData, PropertyDecodedData, BookingPropertyData


class CheckPropertiesUniqueManage:
    """
    Получение всех задублированных объектов недвижимости кабинета со сделками, разбитых на группы.
    """

    correct_property_types: list = [
        "GlobalFlatType",
        "GlobalPantryType",
        "GlobalParkingSpaceType",
        "GlobalCommercialSpaceType",
    ]

    def __init__(self) -> None:
        self.global_id_decoder = from_global_id
        self.property_repo: properties_repos.PropertyRepo = properties_repos.PropertyRepo()
        self.booking_repo: bookings_repos.BookingRepo = bookings_repos.BookingRepo()
        self.interests_repo: users_repos.InterestsRepo = users_repos.InterestsRepo()

        self.orm_class: Type[Tortoise] = Tortoise
        self.orm_config: dict[str, Any] = copy(tortoise_config)
        self.orm_config.pop("generate_schemas", None)

        self.logger: structlog.BoundLogger = structlog.get_logger(__name__)

    async def __call__(self, *args, **kwargs) -> None:
        await self.orm_class.init(config=self.orm_config)
        delete_property_option: str = args[0] if args else None

        properties_global_ids: list[str] = await self.property_repo.list().values_list("global_id", flat=True)
        self.logger.info(
            f"Найдено всего объектов недвижимости (по global_id), в количестве - {len(properties_global_ids)} шт."
        )
        properties_data, incorrect_global_ids = self._get_properties_decoded_data(
            global_ids=properties_global_ids,
        )
        self.logger.info(
            f"Расшифрованы и сгруппированы (по profitbase_id) объекты недвижимости, в количестве - "
            f"{len(properties_data)} шт.\n"
        )
        if incorrect_global_ids:
            await self._get_incorrect_global_id_info(
                incorrect_global_ids=incorrect_global_ids,
                delete_property_option=delete_property_option,
            )

        doubles_properties_data_with_bookings = await self._get_doubles_properties_data_with_bookings(
            properties_data=properties_data,
        )
        self.logger.info(
            f"Задублированные и сгруппированные (по profitbase_id) объекты недвижимости со сделками, в количестве - "
            f"{len(doubles_properties_data_with_bookings)} шт.\n"
        )

        separated_doubles_properties_data = self._separate_doubles_properties_data_to_groups(
            doubles_properties_data=doubles_properties_data_with_bookings,
        )
        self.logger.info(
            f"Объекты недвижимости со сделками только в дублях с корректным типом объекта, в количестве - "
            f"{len(separated_doubles_properties_data['deals_in_correct_property_type'])} шт.\n"
            f"Список объектов - {separated_doubles_properties_data['deals_in_correct_property_type']}\n"
        )
        self.logger.info(
            f"Объекты недвижимости со сделками только в дублях с некорректным типом объекта, в количестве - "
            f"{len(separated_doubles_properties_data['deals_in_incorrect_property_type'])} шт.\n"
            f"Список объектов - {separated_doubles_properties_data['deals_in_incorrect_property_type']}\n"
        )
        self.logger.info(
            f"Объекты недвижимости со сделками в дублях с корректным и некорректным типом объекта, в количестве - "
            f"{len(separated_doubles_properties_data['deals_in_correct_and_incorrect_property_type'])} шт.\n"
            f"Список объектов - {separated_doubles_properties_data['deals_in_correct_and_incorrect_property_type']}\n"
        )
        self.logger.info(
            f"Объекты недвижимости, у которых есть несколько дублей с корректным типом объекта, в количестве - "
            f"{len(separated_doubles_properties_data['property_has_several_correct_types'])} шт.\n"
            f"Список объектов - {separated_doubles_properties_data['property_has_several_correct_types']}\n"
        )
        self.logger.info(
            f"Объекты недвижимости, у которых нет дублей с корректным типом объекта, в количестве - "
            f"{len(separated_doubles_properties_data['property_has_no_correct_types'])} шт.\n"
            f"Список объектов - {separated_doubles_properties_data['property_has_no_correct_types']}\n"
        )
        self.logger.info(
            f"Объекты недвижимости, у которых нет сделок в дублях, в количестве - "
            f"{len(separated_doubles_properties_data['property_without_deals'])} шт.\n"
            f"Список объектов - {separated_doubles_properties_data['property_without_deals']}\n"
        )

        await self._get_doubles_properties_without_bookings_info(
            doubles_properties_data_with_bookings=doubles_properties_data_with_bookings,
            delete_property_option=delete_property_option,
        )

        await self.orm_class.close_connections()

    def _get_properties_decoded_data(self, global_ids: list[str]) -> tuple[dict, list]:
        """
        Получение расшифрованных данных объектов недвижимости, сгруппированных по profitbase_id (property_id).
        """

        properties_data = {}
        incorrect_global_ids = []
        for global_id in global_ids:
            try:
                property_type, property_id = self.global_id_decoder(global_id=global_id)

                # проверяем, что у сделки корректный тип, полученный при расшифровке global_id
                if property_type in self.correct_property_types:
                    is_correct_property_type = True
                else:
                    is_correct_property_type = False

                property_data: PropertyDecodedData = PropertyDecodedData(
                    global_id=global_id,
                    type=property_type,
                    is_correct_type=is_correct_property_type,
                )
                property_id_data: PropertyIdData = PropertyIdData(id=property_id)

                if properties_data.get(property_id_data):
                    properties_data[property_id_data].append(property_data)
                else:
                    properties_data[property_id_data] = [property_data]
            except (binascii.Error, UnicodeDecodeError, ValidationError):
                incorrect_global_ids.append(global_id)

        return properties_data, incorrect_global_ids

    async def _get_incorrect_global_id_info(
        self,
        incorrect_global_ids: list[str],
        delete_property_option: str | None,
    ) -> None:
        """
        Получение дополнительных данных по некорректным (нерасшифрованным) global_id).
        """

        self.logger.info(
            f"Некорректные (нерасшифрованные) global_id объектов недвижимости, в количестве - "
            f"{len(incorrect_global_ids)} шт.\n"
            f"Список некорректных global_id - {incorrect_global_ids}"
        )

        # находим сделки с некорректными объектами недвижимости (с нерасшифрованными global_id)
        bookings_with_incorrect_property_global_id = await self.booking_repo.list(
            filters=dict(property__global_id__in=incorrect_global_ids),
        ).values_list("id", "property__global_id")
        self.logger.info(
            f"Сделки с некорректными (нерасшифрованными global_id) объектами недвижимости, в количестве - "
            f"{len(bookings_with_incorrect_property_global_id)} шт.\n"
            f"Список сделок - {bookings_with_incorrect_property_global_id}\n"
        )

        # оставляем только некорректные (нерасшифрованные) global_id объектов недвижимости без сделок
        incorrect_global_ids_for_property_with_bookings = [
            booking_with_incorrect_property_global_id[1] for booking_with_incorrect_property_global_id
            in bookings_with_incorrect_property_global_id
        ]
        incorrect_global_ids_for_property_without_bookings = []
        for incorrect_global_id in incorrect_global_ids:
            if incorrect_global_id not in incorrect_global_ids_for_property_with_bookings:
                incorrect_global_ids_for_property_without_bookings.append(incorrect_global_id)

        self.logger.info(
            f"Некорректные (нерасшифрованные) global_id объектов недвижимости без сделок, в количестве - "
            f"{len(incorrect_global_ids_for_property_without_bookings)} шт.\n"
            f"Список некорректных global_id объектов недвижимости без сделок - "
            f"{incorrect_global_ids_for_property_without_bookings}\n"
        )

        if delete_property_option == "delete_incorrect_global_ids":
            await self._delete_properties_with_incorrect_global_id_without_bookings(
                incorrect_global_ids=incorrect_global_ids_for_property_without_bookings,
            )

    async def _delete_properties_with_incorrect_global_id_without_bookings(
        self,
        incorrect_global_ids: list[str],
    ) -> None:
        """
        Удаление объектов недвижимости с некорректными (нерасшифрованными global_id) без сделок.
        """

        properties_with_incorrect_global_id_without_bookings = await self.property_repo.list(
            filters=dict(global_id__in=incorrect_global_ids),
        )

        # дополнительный "предохранитель" - итоговая проверка на наличие сделок в удаляемых объектах
        deleted_properties_have_bookings = await self.booking_repo.exists(
            filters=dict(property__global_id__in=incorrect_global_ids),
        )

        if not deleted_properties_have_bookings:
            # сначала удаляем объектов недвижимости с некорректными global_id без сделок из избранного
            user_interest_for_properties_with_incorrect_global_id_without_bookings: list[users_repos.UsersInterests] = \
                await self.interests_repo.list(
                    filters=dict(property__global_id__in=incorrect_global_ids),
                )
            self.logger.info(
                f"Избранное к удалению, у объектов которого некорректный global_id и нет сделок, в количестве - "
                f"{len(user_interest_for_properties_with_incorrect_global_id_without_bookings)} шт.\n"
            )
            for user_interest in user_interest_for_properties_with_incorrect_global_id_without_bookings:
                await self.interests_repo.delete(user_interest)

            self.logger.info(
                f"Объекты недвижимости к удалению, у которых некорректный global_id и нет сделок, в количестве - "
                f"{len(properties_with_incorrect_global_id_without_bookings)} шт.\n"
            )
            for property in properties_with_incorrect_global_id_without_bookings:
                await self.property_repo.delete(property)

    async def _get_doubles_properties_data_with_bookings(self, properties_data: dict) -> dict:
        """
        Получение только задублированных данных объектов недвижимости вместе со сделками,
        сгруппированных по profitbase_id (property_id).
        """

        # находим задублированные объекты недвижимости
        doubles_properties_data = {
            key: value for key, value in properties_data.items() if len(value) > 1
        }

        # находим global_id всех задублированных объектов недвижимости
        doubles_property_global_ids = []
        for doubles_property_data in doubles_properties_data.values():
            for property_data in doubles_property_data:
                doubles_property_global_ids.append(property_data.global_id)

        # находим сделки с задублированными объектами недвижимости
        booking_doubles_properties_data = await self.booking_repo.list(
            filters=dict(property__global_id__in=doubles_property_global_ids),
        ).values_list("id", "property__global_id")

        # связываем полученные сделки с дублями объектов недвижимости
        for doubles_property_data in doubles_properties_data.values():
            for property_data in doubles_property_data:
                for booking_doubles_property in booking_doubles_properties_data:
                    if property_data.global_id == booking_doubles_property[1]:
                        property_data.bookings.append(
                            BookingPropertyData(
                                id=booking_doubles_property[0],
                                property_global_id=booking_doubles_property[1],
                            )
                        )

        return doubles_properties_data

    def _separate_doubles_properties_data_to_groups(self, doubles_properties_data: dict) -> dict:
        """
        Разделение задублированных данных объектов недвижимости вместе со сделками по группам.
        """

        deals_in_correct_property_type = []  # сделки только в дублях с корректным типом объекта
        deals_in_incorrect_property_type = []  # сделки только в дублях с некорректным типом объекта
        deals_in_correct_and_incorrect_property_type = []  # сделки есть в дублях с корректным и некорректным типом
        property_has_several_correct_types = []  # у объекта есть несколько дублей с корректным типом объекта
        property_has_no_correct_types = []  # у объекта нет дублей с корректным типом объекта
        property_without_deals = []  # в дублях объекта нет сделок

        for property_id, doubles_property_data in doubles_properties_data.items():
            correct_type_count = 0
            is_deals_in_correct_property_type = False
            is_deals_in_incorrect_property_type = False

            for property_data in doubles_property_data:
                if property_data.is_correct_type:
                    correct_type_count += 1
                    if property_data.bookings:
                        is_deals_in_correct_property_type = True
                elif property_data.bookings:
                    is_deals_in_incorrect_property_type = True

            if correct_type_count > 1:
                property_has_several_correct_types.append(property_id)
            elif correct_type_count == 0:
                property_has_no_correct_types.append(property_id)
            elif is_deals_in_correct_property_type and is_deals_in_incorrect_property_type:
                deals_in_correct_and_incorrect_property_type.append(property_id)
            elif is_deals_in_correct_property_type:
                deals_in_correct_property_type.append(property_id)
            elif is_deals_in_incorrect_property_type:
                deals_in_incorrect_property_type.append(property_id)
            else:
                property_without_deals.append(property_id)

        return dict(
            deals_in_correct_property_type={
                key: value for key, value in doubles_properties_data.items()
                if key in deals_in_correct_property_type
            },
            deals_in_incorrect_property_type={
                key: value for key, value in doubles_properties_data.items()
                if key in deals_in_incorrect_property_type
            },
            deals_in_correct_and_incorrect_property_type={
                key: value for key, value in doubles_properties_data.items()
                if key in deals_in_correct_and_incorrect_property_type
            },
            property_has_several_correct_types={
                key: value for key, value in doubles_properties_data.items()
                if key in property_has_several_correct_types
            },
            property_has_no_correct_types={
                key: value for key, value in doubles_properties_data.items()
                if key in property_has_no_correct_types
            },
            property_without_deals={
                key: value for key, value in doubles_properties_data.items()
                if key in property_without_deals
            },
        )

    async def _get_doubles_properties_without_bookings_info(
        self,
        doubles_properties_data_with_bookings: dict,
        delete_property_option: str | None,
    ) -> None:
        """
        Получение списка и количества global_id для дублей объектов недвижимости без сделок.
        """

        global_ids_for_double_property_with_bookings = []
        global_ids_for_double_property_without_bookings = []
        for property_id, doubles_property_data in doubles_properties_data_with_bookings.items():
            for property_data in doubles_property_data:
                if not property_data.bookings:
                    global_ids_for_double_property_without_bookings.append(property_data.global_id)
                else:
                    global_ids_for_double_property_with_bookings.append(property_data.global_id)

        self.logger.info(
            f"Global id задублированных объектов недвижимости со сделками, в количестве - "
            f"{len(global_ids_for_double_property_with_bookings)} шт.\n"
            f"Список global_id задублированных объектов недвижимости со сделками - "
            f"{global_ids_for_double_property_with_bookings}\n"
        )
        self.logger.info(
            f"Global id задублированных объектов недвижимости без сделок, в количестве - "
            f"{len(global_ids_for_double_property_without_bookings)} шт.\n"
            f"Список global_id задублированных объектов недвижимости без сделок - "
            f"{global_ids_for_double_property_without_bookings}\n"
        )

        if delete_property_option == "delete_doubles_properties":
            await self._delete_doubles_properties_without_bookings(
                global_ids_for_double_property_without_bookings=global_ids_for_double_property_without_bookings,
            )

    async def _delete_doubles_properties_without_bookings(
        self,
        global_ids_for_double_property_without_bookings: list[str],
    ) -> None:
        """
        Удаление дублей объектов недвижимости без сделок.
        """

        doubles_properties_without_bookings = await self.property_repo.list(
            filters=dict(global_id__in=global_ids_for_double_property_without_bookings),
        )

        # дополнительный "предохранитель" - итоговая проверка на наличие сделок в удаляемых объектах
        deleted_properties_have_bookings = await self.booking_repo.exists(
            filters=dict(property__global_id__in=global_ids_for_double_property_without_bookings),
        )

        if not deleted_properties_have_bookings:
            # сначала удаляем дубли объектов недвижимости без сделок из избранного
            user_interests_for_doubles_properties_without_bookings: list[users_repos.UsersInterests] = \
                await self.interests_repo.list(
                    filters=dict(property__global_id__in=global_ids_for_double_property_without_bookings),
                )
            self.logger.info(
                f"Избранное к удалению, у объектов которого есть дубли и нет сделок, в количестве - "
                f"{len(user_interests_for_doubles_properties_without_bookings)} шт.\n"
            )
            for user_interest in user_interests_for_doubles_properties_without_bookings:
                await self.interests_repo.delete(user_interest)

            self.logger.info(
                f"Дубли объектов недвижимости к удалению, у которых нет сделок, в количестве - "
                f"{len(doubles_properties_without_bookings)} шт.\n"
            )
            for doubles_property in doubles_properties_without_bookings:
                await self.property_repo.delete(doubles_property)
