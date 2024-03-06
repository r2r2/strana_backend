"""
AMOCRM components
"""
from abc import ABC
from datetime import datetime, timedelta
from enum import IntEnum
from typing import Any, Optional, Union

import jmespath
import structlog
from common.amocrm.components.interface import AmoCRMInterface
from config import EnvTypes, maintenance_settings
from pydantic import ValidationError, parse_obj_as
from pytz import UTC
from starlette import status as http_status

from config.feature_flags import FeatureFlags
from ...requests import CommonResponse
from ..constants import AmoLeadQueryWith, BaseLeadSalesStatuses
from ..exceptions import AmocrmHookError
from ..leads.payment_method import AmoCRMPaymentMethod, AmoCRMPaymentMethodMapping
from ..models import Entity
from ..types import AmoCustomField, AmoCustomFieldValue, AmoLead, AmoTag
from ..types.lead import AmoLeadCompany, AmoLeadContact, AmoLeadEmbedded
from .decorators import user_tag_test_wrapper
from ...sentry.utils import send_sentry_log
from ...unleash.client import UnleashClient


class AmoCRMLeads(AmoCRMInterface, ABC):
    """
    AmoCRM leads integration
    """

    def __init__(self,
                 logger: Optional[Any] = structlog.getLogger(__name__)):
        self.logger = logger

    class PipelineIds(IntEnum):
        CALL_CENTER: int = 3934218
        TYUMEN: int = 1305043
        MOSCOW: int = 1941865
        SPB: int = 3568449
        EKB: int = 5798376
        TEST: int = 4623009

    city_name_mapping: dict[str, str] = {
        "Тюмень": "tmn",
        "Санкт-Петербург": "spb",
        "Москва": "msk",
        "Екатеринбург": "ekb",
        "Не определен": "test_case",
    }

    price_payed_map: dict[int, bool] = {
        1309975: True,
        1309977: False,
    }

    # Common attributes
    default_lead_name: str = "Бронирование"

    # Registration attributes
    start_status_id: int = 37592457
    start_pipeline_id: int = 3934218
    start_responsible_user: int = 6689880
    start_tags: list[str] = ["Регистрация ЛК"]

    # Creation attributes
    _lead_tags: list[str] = []

    # Showtime attributes
    showtime_name: str = "Запись на показ"
    showtime_status_id: int = 37592457
    showtime_pipeline_id: int = 3934218
    showtime_responsible_user: int = 6689880
    showtime_datetime_field_id: int = 689581
    showtime_process_status_id: int = 37592541

    # Custom fields
    agent_field_id: int = 643291
    commission: int = 822836  # Процент риелтора
    commission_value: int = 812300  # Вознаграждение риелтора (сумма в руб)
    city_field_id: int = 692726
    project_field_id: int = 596489
    property_field_id: int = 363971
    organization_field_id: int = 641685
    property_type_field_id: int = 366965
    property_str_type_field_id: int = 690114
    booking_start_field_id: int = 689005
    booking_end_field_id: int = 689007
    booking_price_field_id: int = 689009
    booking_payment_status_field_id: int = 689011
    booking_payment_field_id: int = 683435
    booking_type_field_id: int = 826868
    booking_bill_paid_field_id: int = 823344
    booking_discount_price_field_id: int = 823704
    # Размер скидки/акции
    booking_discounts_and_promotions: int = 575381
    # Общий размер скидки
    booking_final_discount_field_id = 831658
    # Общая стоимость доп. опций
    booking_final_additional_options_field_id = 831660
    #: Статус онлайн-покупки
    booking_online_purchase_status_field_id: int = 823792
    #: Дата и время начала онлайн-покупки
    booking_online_purchase_start_datetime_field_id: int = 823794
    #: Тип оплаты ('способ покупки' в нашем коде)
    booking_payment_type_field_id: int = 366639
    #: Есть ли у клиента одобренная ипотека
    booking_is_mortgage_approved_field_id: int = 688723
    #: Url на форму для загрузки ДДУ юристом
    booking_ddu_upload_url_field_id: int = 823790
    #: Дата и время отправки документов на регистрацию
    booking_send_documents_datetime_field_id: int = 823796
    #: ID онлайн-покупки
    booking_online_purchase_id_field_id: int = 823802
    #: Дата и время согласования договора
    booking_ddu_acceptance_datetime_field_id: int = 823798
    #: Текущий статус с этой даты и времени
    status_from_datetime_field_id: int = 828938
    #: Были ли на статусе Фиксация за АН
    assign_agency_status_field_id: int = 828940
    booking_expires_datetime_field_id: int = 643043
    booking_is_agency_deal_field_id: int = 814164  # Сделка с Агентством?
    house_field_id: int = 363959  # Дом
    room_number_field_id: int = 363965  # Номер помещения

    # ID полей для встреч
    meeting_type_field_id = 815568
    meeting_date_next_contact_field_id = 694314
    meeting_date_sensei_field_id = 689581
    meeting_link_field_id = 833402
    meeting_date_zoom_field_id = 688593
    meeting_address_field_id = 831168
    meeting_property_type_field_id = 366965
    meeting_user_name_field_id = 676461
    meeting_type_next_contact_field_id = 694316
    commercial_offer_field_id = 826886
    meeting_types_next_contact_map: dict[str, dict[str, int | str]] = {
        "Meet": {"enum_id": 1323738, "value": "Встреча"},
        "ZOOM": {"enum_id": 1325614, "value": "Назначить ZOOM КЦ"},
    }
    meeting_types: dict[str, str] = {
        "1326776": "online",
        "1326774": "offline",
    }
    meeting_property_types: dict[str, str] = {
        "715523": "flat",
        "715525": "parking",
        "1311059": "commercial",
        "1331542": "pantry",
        "1324118": "apartment",
    }

    # Env теги
    dev_test_lead_tag: list[str] = ['Тестовая бронь']
    stage_test_lead_tag: list[str] = ['Тестовая бронь Stage']

    # ID Тегов
    fast_booking_tag_id: int = 748608
    dev_booking_tag_id: int = 708334
    stage_booking_tag_id: int = 765058
    dev_contact_tag_id: int = 741628
    stage_contact_tag_id: int = 788570

    # Lead contacts tags IDs
    realtor_tag_id: int = 437407
    client_tag_id: int = 555355

    # ID Условия_оплаты_брони
    booking_type_20_days: int = 1
    booking_type_50_days: int = 2
    booking_type_14_days: int = 3

    # Distinct statuses
    realized_status_id: int = 142
    unrealized_status_id: int = 143

    # Custom fields values
    city_field_values: dict[str, dict[str, Union[str, int]]] = {
        "tmn": {"enum_id": 1322598, "value": "Тюмень"},
        "msk": {"enum_id": 1322604, "value": "Москва"},
        "spb": {"enum_id": 1322602, "value": "Санкт-Петербург"},
        "ekb": {"enum_id": 1322600, "value": "Екатеринбург"},
        "test_case": {"enum_id": 1332428, "value": "Не определен"},
    }
    property_type_field_values: dict[str, dict[str, Union[str, int]]] = {
        "flat": {"enum_id": 715523, "value": "Квартира"},
        "parking": {"enum_id": 715525, "value": "Паркинг"},
        "commercial": {"enum_id": 1311059, "value": "Коммерция"},
        "commercial_apartment": {"enum_id": 1324118, "value": "Апартаменты"},
        "apartment": {"enum_id": 1324118, "value": "Апартаменты"},
        "pantry": {"enum_id": 1331542, "value": "Кладовка"},
    }
    property_str_type_reverse_values: dict[str, str] = {
        "Квартира": "FLAT",
        "Кладовка": "PANTRY",
        "Паркинг": "PARKING",
        "Машиноместо": "PARKING",
        "Коммерция": "COMMERCIAL",
        "Апартаменты": "APARTMENT",
        "Апартаменты коммерции": "COMMERCIAL_APARTMENT",
    }
    global_types_mapping: dict[str, str] = {
        "FLAT": "GlobalFlatType",
        "PANTRY": "GlobalPantryType",
        "PARKING": "GlobalParkingSpaceType",
        "COMMERCIAL_APARTMENT": "GlobalFlatType",
        "COMMERCIAL": "GlobalCommercialSpaceType",
        "APARTMENT": "GlobalFlatType",
    }
    booking_payment_types_values: dict[int, dict[str, Union[str, int]]] = {
        714853: {"enum_id": 714853, "value": "100%"},
        714855: {"enum_id": 714855, "value": "Ипотека"},
        714857: {"enum_id": 714857, "value": "Ипотека субсидированная"},
        714859: {"enum_id": 714859, "value": "наличные+ МСК"},
        714861: {"enum_id": 714861, "value": "Рассрочка"},
        714863: {"enum_id": 714863, "value": "Сертификат"},
        1284003: {"enum_id": 1284003, "value": "Ипотека+МСК"},
        1324226: {"enum_id": 1324226, "value": "Рассрочка+МСК"},
        1315751: {"enum_id": 1315751, "value": "Ипотека +сертификат"},
        1315753: {"enum_id": 1315753, "value": "Наличные+сертификат"},
        1317511: {"enum_id": 1317511, "value": "Наличные+сертификат+займ"},
        1317513: {"enum_id": 1317513, "value": "Наличные+ипотека+сертификат+займ"},
        1317551: {"enum_id": 1317551, "value": "Наличные+сертификат+займ+МСК"},
        1317705: {"enum_id": 1317705, "value": "Ипотека субсидированная"},
        1318019: {"enum_id": 1318019, "value": "Ипотека несубсидированная"},
        1324558: {"enum_id": 1324558, "value": "Цена за наличные"},
        1326788: {"enum_id": 1326788, "value": "Ипотека несубсидированная"},
        1330204: {"enum_id": 1330204, "value": "Ипотека субсидированная"},
        1333270: {"enum_id": 1333270, "value": "Цена за наличные"},
        1338116: {"enum_id": 1338116, "value": "Ипотека несубсидированная"},
        1338552: {"enum_id": 1338552, "value": "Ипотека несубсидированная"},
        1338556: {"enum_id": 1338556, "value": "Цена за наличные"},
    }

    online_purchase_status_map = {
        "started": {
            "enum": 1331494,
            "value": "приступил к онлайн-покупке",
        },
        "docs_sent": {
            "enum": 1331496,
            "value": "отправил документы на регистрацию",
        },
        "ddu_accepted": {
            "enum": 1331498,
            "value": "согласовал договор",
        },
        "ddu_registered": {
            "enum": 1331500,
            "value": "договор зарегистрирован",
        },
    }

    # Purchase field mapping
    purchase_field_mapping: dict[int, bool] = {
        1309975: True,
        1309977: False,
    }

    # Reverse type converter
    property_type_reverse_values: dict[int, str] = {
        715523: "FLAT",
        715525: "PARKING",
        1311059: "COMMERCIAL",
        1324118: "COMMERCIAL_APARTMENT",
        1331542: "PANTRY",
    }
    property_final_price_field_id: int = 679313
    property_price_with_sale_field_id: int = 575401

    class CallCenterStatuses(BaseLeadSalesStatuses, IntEnum):
        """
        Call Center statuses
        """
        UNASSEMBLED: int = 37592454  # Неразобранное
        START: int = 37592457  # Первичный контакт
        START_2: int = 55148413  # Первичный контакт 2
        ASSIGN_AGENT: int = 62123581  # Фиксация клиента за ан
        THINKING_ABOUT_PRICE: int = 51568512  # думает над ценой
        SEEKING_MONEY: int = 51568509  # ищет деньги
        CONTACT_AFTER_BOT: int = 60225745  # связаться после бота
        SUCCESSFUL_BOT_CALL_TRANSFER: int = 57451585  # Успешный перевод звонка бота
        REFUSE_MANGO_BOT: int = 59857493  # Отказ Mango бота
        REDIAL: int = 39338919  # Автодозвон
        RESUSCITATED_CLIENT: int = 51568251  # Реанимированный клиент
        SUBMIT_SELECTION: int = 51568125  # Отправить подборку
        ROBOT_CHECK: int = 39339075  # Проверка робота
        TRY_CONTACT: int = 37592460  # Попытка связаться
        QUALITY_CONTROL: int = 39394839  # Контроль качества
        SELL_APPOINTMENT: int = 40127289  # Продай встречу
        GET_TO_MEETING: int = 39394842  # Дожать на встречу
        MAKE_APPOINTMENT: int = 37592463  # Назначить встречу
        APPOINTED_ZOOM: int = 40127292  # Назначен ZOOM
        ZOOM_CALL: int = 40127295  # Идет ZOOM
        THINKING_OF_MORTGAGE: int = 51568506  # Думает над ипотекой
        MAKE_DECISION: int = 40127307  # Принимают решение
        BOOKING: int = 40127310  # Бронь
        PAID_BOOKING: int = 0  # платная бронь
        APPOINTMENT: int = 37592541  # Назначена встреча
        TRANSFER_MANAGER: int = 37592544  # Передать менеджеру
        REALIZED: int = 142  # Успешно реализовано
        UNREALIZED: int = 143  # Закрыто и не реализовано

    class TMNStatuses(BaseLeadSalesStatuses, IntEnum):
        """
        TMN statuses
        """
        START: int = 21189703  # первичный контакт
        MAKE_APPOINTMENT: int = 40850073  # Назначить встречу
        ASSIGN_AGENT: int = 51489690  # фиксация клиента за ан
        MEETING: int = 21189706  # Встреча назначена
        MEETING_IN_PROGRESS: int = 21189709  # Идёт встреча
        MAKE_DECISION: int = 21189712  # Принимают решение
        RE_MEETING: int = 40850076  # Повторная встреча
        BOOKING: int = 21197641  # бронь
        PAID_BOOKING: int = 40850079  # платная бронь
        APPLY_FOR_A_MORTGAGE: int = 40850085  # подать на ипотеку
        MORTGAGE_FILED: int = 21199108  # ипотека подана
        MORTGAGE_DONE: int = 28972285  # ипотека одобрена
        DDU_PROCESS: int = 21197560  # оформление дду
        DDU_SIGNING: int = 21199072  # подписание дду
        DDU_REGISTER: int = 21197563  # мфц
        MONEY_PROCESS: int = 21197566  # зачисление денег
        REALIZED: int = 142  # успешно реализовано
        TERMINATION: int = 34654647  # расторжение
        UNREALIZED: int = 143  # Закрыто и не реализовано

    class MSKStatuses(BaseLeadSalesStatuses, IntEnum):
        """
        MSK statuses
        """
        START: int = 29096287  # Первичный контакт
        ASSIGN_AGENT: int = 51105825  # фиксация клиента за ан
        MAKE_APPOINTMENT: int = 29096290  # Назначить встречу
        MEETING: int = 45598248  # Встреча назначена
        MEETING_IN_PROGRESS: int = 45598251  # Идёт встреча
        MAKE_DECISION: int = 29096398  # Принимают решение
        RE_MEETING: int = 45598254  # Повторная встреча
        BOOKING: int = 29096401  # Бронь
        PAID_BOOKING: int = 45598284  # Платная бронь
        MORTGAGE_LEAD: int = 29096404  # Заявка на ипотеку
        APPLY_FOR_A_MORTGAGE: int = 29096404  # Подать на ипотеку
        MORTGAGE_FILED: int = 45598290  # Ипотека подана
        MORTGAGE_DONE: int = 45598293  # Ипотека одобрена
        DDU_PROCESS: int = 29096407  # Оформление ДДУ
        CONFIRMATION: int = 29096410  # Согласование
        DDU_SIGNING: int = 29096413  # Подписание ДДУ с клиентом
        DDU_REGISTER: int = 29096416  # МФЦ
        MONEY_PROCESS: int = 29096419  # Зачисление денег
        REALIZED: int = 142  # Успешно реализовано
        UNREALIZED: int = 143  # Закрыто и не реализовано

    class SPBStatuses(BaseLeadSalesStatuses, IntEnum):
        """
        SPB statuses
        """
        START: int = 35065581  # первичный контакт
        ASSIGN_AGENT: int = 41481162  # Фиксация клиента за агентом
        MAKE_APPOINTMENT: int = 41182440  # Назначить встречу
        MEETING: int = 36204951  # Встреча назначена
        MEETING_IN_PROGRESS: int = 41182452  # Идёт встреча
        MAKE_DECISION: int = 36204954  # Принимают решение
        RE_MEETING: int = 41182443  # Повторная встреча
        BOOKING: int = 35065584  # Бронь
        PAID_BOOKING: int = 41182425  # Платная бронь
        APPLY_FOR_A_MORTGAGE: int = 35065587  # Подать на ипотеку
        MORTGAGE_FILED: int = 41182434  # Ипотека подана
        MORTGAGE_DONE: int = 41182437  # Ипотека одобрена
        DDU_PROCESS: int = 36204957  # Оформление ДДУ
        CONFIRMATION: int = 36204960  # Согласование
        DDU_SIGNING: int = 36204963  # Подписание дду с клиентом
        DDU_REGISTER: int = 36204966  # МФЦ
        MONEY_PROCESS: int = 36204969  # Зачисление денег
        TERMINATION: int = 41182407  # РАСТОРЖЕНИЕ
        REALIZED: int = 142  # Успешно реализовано
        UNREALIZED: int = 143  # Закрыто и не реализовано

    class EKBStatuses(BaseLeadSalesStatuses, IntEnum):
        """
        EKB statuses
        """
        START: int = 50814837  # первичный контакт
        ASSIGN_AGENT: int = 51944400  # Фиксация клиента за агентом
        MAKE_APPOINTMENT: int = 50814840  # Назначить встречу
        MEETING: int = 50814930  # Встреча назначена
        MEETING_IN_PROGRESS: int = 50814843  # Идёт встреча
        MAKE_DECISION: int = 50814933  # Принимают решение
        RE_MEETING: int = 50814936  # Повторная встреча
        BOOKING: int = 50814939  # Бронь
        PAID_BOOKING: int = 50814942  # Платная бронь
        APPLY_FOR_A_MORTGAGE: int = 50814948  # Подать на ипотеку
        MORTGAGE_FILED: int = 50814951  # Ипотека подана
        MORTGAGE_DONE: int = 50814954  # Ипотека одобрена
        DDU_PROCESS: int = 50814957  # Оформление ДДУ
        DDU_SIGNING: int = 50814960  # Подписание дду с клиентом
        DDU_REGISTER: int = 50814963  # МФЦ
        MONEY_PROCESS: int = 50814966  # Зачисление денег
        TERMINATION: int = 50814969  # РАСТОРЖЕНИЕ
        REALIZED: int = 142  # Успешно реализовано
        UNREALIZED: int = 143  # Закрыто и не реализовано

    class TestStatuses(BaseLeadSalesStatuses, IntEnum):
        """
        Test statuses
        """
        START: int = 42477861  # Первичный контракт
        REDIAL: int = 50284797  # Автодозвон
        ROBOT_CHECK: int = 50284800  # Проверка робота
        TRY_CONTACT: int = 50284803  # Попытка связаться
        QUALITY_CONTROL: int = 50284806  # Контроль качества
        SELL_APPOINTMENT: int = 50284809  # Продай встречу
        GET_TO_MEETING: int = 50284812  # Дожать на встречу
        ASSIGN_AGENT: int = 50284815  # Фиксация клиента за агентом
        MAKE_APPOINTMENT: int = 50228688  # Назначить встречу
        APPOINTED_ZOOM: int = 50284818  # Назначен ZOOM
        MEETING_IS_SET: int = 50228691  # встреча назначена
        ZOOM_CALL: int = 40127295  # Идет ZOOM
        MEETING_IN_PROGRESS: int = 50228694  # Идёт встреча
        MAKE_DECISION: int = 42477867  # Принимают решение
        RE_MEETING: int = 50228697  # Повторная встреча
        BOOKING: int = 42477951  # Бронь
        APPOINTMENT: int = 50284824  # Назначена встреча
        TRANSFER_MANAGER: int = 50284827  # Передать менеджеру
        PAID_BOOKING: int = 50228700  # Платная бронь
        REBOOKING: int = 50228703  # Перебронь
        APPLY_FOR_A_MORTGAGE: int = 50228706  # Подать на ипотеку
        MORTGAGE_FILED: int = 50228709  # Ипотека подана
        MORTGAGE_DONE: int = 50228712  # Ипотека одобрена
        DDU_PROCESS: int = 50228715  # Оформление ДДУ
        DDU_SIGNING: int = 50228718  # Подписание дду с клиентом
        DDU_REGISTER: int = 50228721  # МФЦ
        MONEY_PROCESS: int = 50228724  # Зачисление денег
        TERMINATION: int = 50228727  # РАСТОРЖЕНИЕ
        REALIZED: int = 142  # Успешно реализовано
        UNREALIZED: int = 143  # Закрыто и не реализовано

    # Leads statuses for call center
    # Pipeline ID: 3934218
    call_center_status_ids: dict[str, int] = {
        status.name.lower(): status.value for status in CallCenterStatuses
        if status.value is not None
    }

    # Leads statuses by city
    # Pipeline ID: 1305043
    tmn_status_ids: dict[str, int] = {
        status.name.lower(): status.value for status in TMNStatuses
        if status.value is not None
    }

    # Pipeline ID: 1941865
    msk_status_ids: dict[str, int] = {
        status.name.lower(): status.value for status in MSKStatuses
        if status.value is not None
    }

    # Pipeline ID: 3568449
    spb_status_ids: dict[str, int] = {
        status.name.lower(): status.value for status in SPBStatuses
        if status.value is not None
    }

    # Pipeline ID: 5798376
    ekb_status_ids: dict[str, int] = {
        status.name.lower(): status.value for status in EKBStatuses
        if status.value is not None
    }

    # Pipeline ID: 4623009
    test_case_status_ids: dict[str, int] = {
        status.name.lower(): status.value for status in TestStatuses
        if status.value is not None
    }

    tmn_import_status_ids: set[int] = set(tmn_status_ids.values())
    msk_import_status_ids: set[int] = set(msk_status_ids.values())
    spb_import_status_ids: set[int] = set(spb_status_ids.values())
    ekb_import_status_ids: set[int] = set(ekb_status_ids.values())
    test_import_status_ids: set[int] = set(test_case_status_ids.values())
    call_center_import_status_ids: set[int] = set(call_center_status_ids.values())

    tmn_substages: dict[int, str] = {value: key for key, value in tmn_status_ids.items()}
    msk_substages: dict[int, str] = {value: key for key, value in msk_status_ids.items()}
    spb_substages: dict[int, str] = {value: key for key, value in spb_status_ids.items()}
    ekb_substages: dict[int, str] = {value: key for key, value in ekb_status_ids.items()}
    test_case_substages: dict[int, str] = {value: key for key, value in test_case_status_ids.items()}
    call_center_substages: dict[int, str] = {value: key for key, value in call_center_status_ids.items()}

    # Common pipelines
    sales_pipeline_ids: set[int] = {
        PipelineIds.SPB,
        PipelineIds.TYUMEN,
        PipelineIds.MOSCOW,
        PipelineIds.EKB,
        PipelineIds.TEST,
        PipelineIds.CALL_CENTER,
    }

    common_pipeline_ids: set[int] = {id.value for id in PipelineIds}

    # Cities mapping by slug
    lead_city_mapping: dict[str, str] = {
        "spb": "spb",
        "tmn": "tmn",
        "msk": "msk",
        "ekb": "ekb",
        "test_case": "test_case",
    }

    async def fetch_lead(
            self,
            *,
            lead_id: Union[int, str],
            query_with: list[AmoLeadQueryWith] = None
    ) -> Optional[AmoLead]:
        """
        Lead lookup by id
        """
        if lead_id is None:
            return None
        route: str = f"/leads/{lead_id}"
        query: dict[str, Any] = {}
        if query_with:
            query.update({"with": ",".join(query_with)})

        response: CommonResponse = await self._request_get_v4(route=route, query=query)
        if response.status == http_status.HTTP_204_NO_CONTENT:
            return None
        try:
            return AmoLead.parse_obj(getattr(response, "data", {}))
        except ValidationError as err:
            self.logger.warning(
                f"cabinet/amocrm/fetch_lead: Status {response.status}: "
                f"Пришли неверные данные: {response.data}"
                f"Exception: {err}"
            )
            return None

    async def fetch_leads(
        self,
        *,
        lead_ids: list[int | str],
        query_with: list[AmoLeadQueryWith] | None = None,
        created_at_range: dict[str, int] | None = None,
        pipeline_statuses: list | None = None,
    ) -> list[AmoLead]:
        """
        Lead lookup by id
        """
        if not lead_ids:
            lead_ids = []

        route: str = "/leads"
        query: dict[str, Any] = {
            f"filter[id][{index}]": lead_id for index, lead_id in enumerate(lead_ids)
        }
        if created_at_range is not None:
            query["filter[created_at][from]"] = created_at_range["from"]
            query["filter[created_at][to]"] = created_at_range["to"]

        if pipeline_statuses is not None:
            for index, (pipeline, status) in enumerate(pipeline_statuses):
                if status is not None and pipeline is not None:
                    query[f"filter[statuses][{index}][pipeline_id]"] = pipeline.value
                    query[f"filter[statuses][{index}][status_id]"] = status.value

        if query_with:
            query.update({"with": ",".join(query_with)})
        response: CommonResponse = await self._request_get_v4(route=route, query=query)

        if response.status == http_status.HTTP_204_NO_CONTENT:
            return []
        return await self._parse_leads_data(
            response=response,
            method_name='cabinet/amocrm/fetch_leads',
            payload=query,
        )

    @user_tag_test_wrapper
    async def create_lead(
        self,
        city_slug: str,
        user_amocrm_id: int,
        project_amocrm_responsible_user_id: Union[str, int],
        lead_name: str | None = None,
        project_amocrm_name: Optional[str] = None,
        project_amocrm_enum: Optional[int] = None,
        project_amocrm_pipeline_id: Union[str, int, None] = None,
        project_amocrm_organization: Optional[str] = None,
        property_id: Optional[int] = None,
        property_type: Optional[str] = None,
        contact_ids: Optional[list[int]] = None,
        status: Optional[str] = None,
        status_id: Optional[int] = None,
        tags: list[str] | None = None,
        booking_type_id: Optional[int] = None,
        companies: Optional[list[int]] = None,
        is_agency_deal: Optional[bool] = None,
        payment_type_enum: Optional[int] = None,
    ) -> list[AmoLead]:
        """
        Lead creation
        @param city_slug: str. Короткое название города, например tmn/spb
        @param property_id: int
        @param property_type: str
        @param user_amocrm_id: int. ID пользователя из амо. Будет считаться основным контактом.
        @param project_amocrm_name: str
        @param project_amocrm_enum: str
        @param project_amocrm_organization: str
        @param project_amocrm_pipeline_id: int. ID воронки, в которой находится проект.
        @param project_amocrm_responsible_user_id: str/int - ID ответственного за сделку.
        @param contact_ids: list[int]. Список id контактов из амо, которые закрепим за сделкой.
        @param status: str. Строка статуса BookingSubstages, используется если не передан status_id
        @param status_id: int
        @param tags: list[str]. Список тегов.
        @param booking_type_id: int
        @param companies: Optional[list[int]]. Список id компаний из амо
        @param is_agency_deal: Сделка с Агентством?
        @param lead_name: Название сделки, для общего случая можно использовать метод create_lead_name, он лежит в
        @param payment_type_enum: int
        booking.utils
        @return: list[AmoLead]
        """
        route: str = "/leads"
        if not status_id:
            status_id = getattr(self, f"{self.lead_city_mapping[city_slug]}_status_ids")[status]
        if not lead_name:
            lead_name = self.default_lead_name

        if tags is None:
            tags = []

        if maintenance_settings["environment"] == EnvTypes.DEV:
            self._lead_tags.extend(self.dev_test_lead_tag)
        elif maintenance_settings["environment"] == EnvTypes.STAGE:
            self._lead_tags.extend(self.stage_test_lead_tag)

        tags: list[AmoTag] = [AmoTag(name=tag) for tag in (tags + self._lead_tags)] 
        if companies:
            companies: list[AmoLeadCompany] = [AmoLeadCompany(id=company) for company in companies]
        if not contact_ids:
            contact_ids = []
        contacts: list[AmoLeadContact] = [
            AmoLeadContact(id=user_amocrm_id, is_main=True),
            *[AmoLeadContact(id=contact_id, is_main=False) for contact_id in contact_ids]
        ]
        custom_fields: list[AmoCustomField] = self._get_lead_default_custom_fields(
            city_slug=city_slug,
            property_id=property_id,
            property_type=property_type,
            project_amocrm_name=project_amocrm_name,
            project_amocrm_enum=project_amocrm_enum,
            project_amocrm_organization=project_amocrm_organization,
            booking_type_id=booking_type_id,
            is_agency_deal=is_agency_deal,
            payment_type_enum=payment_type_enum,
        )
        self.logger.debug("AmoCRM create lead", custom_fields=custom_fields)
        payload: AmoLead = AmoLead(
            name=lead_name,
            created_at=int(datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.now(tz=UTC).timestamp()),
            status_id=status_id,
            pipeline_id=project_amocrm_pipeline_id,
            custom_fields_values=custom_fields,
            responsible_user_id=project_amocrm_responsible_user_id,
            _embedded=AmoLeadEmbedded(
                tags=tags,
                contacts=contacts,
                companies=companies,
            )
        )
        response: CommonResponse = await self._request_post_v4(
            route=route, payload=[payload.dict(exclude_unset=True)])
        return await self._parse_leads_data(
            response=response,
            method_name='cabinet/amocrm/create_lead',
            payload=payload,
        )

    async def create_showtime(
        self,
        city_slug: str,
        visit: datetime,
        property_type: str,
        user_amocrm_id: int,
        agent_amocrm_id: int,
        project_amocrm_name: str,
        project_amocrm_enum: int,
    ) -> list[Any]:
        """
        Showtime creation
        """

        route: str = "/leads"
        custom_fields: list[AmoCustomField] = self._get_showtime_custom_fields(
            visit=visit,
            city_slug=city_slug,
            property_type=property_type,
            project_amocrm_name=project_amocrm_name,
            project_amocrm_enum=project_amocrm_enum,
        )
        contacts: list[AmoLeadContact] = [
            AmoLeadContact(id=user_amocrm_id, is_main=True),
            AmoLeadContact(id=agent_amocrm_id, is_main=False),
        ]
        payload: AmoLead = AmoLead(
            name=self.showtime_name,
            created_at=int(datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.now(tz=UTC).timestamp()),
            status_id=self.showtime_status_id,
            pipeline_id=self.showtime_pipeline_id,
            custom_fields_values=custom_fields,
            responsible_user_id=self.showtime_responsible_user,
            _embedded=AmoLeadEmbedded(
                tags=[AmoTag(name="Запись на показ")],
                contacts=contacts,
            )
        )
        response: CommonResponse = await self._request_post_v4(
            route=route, payload=payload.dict(exclude_unset=True))
        return await self._parse_leads_data(
            response=response,
            method_name='cabinet/amocrm/create_showtime',
            payload=payload,
        )

    async def update_lead(self, *args, **kwargs):
        if self.__is_strana_lk_2882_enable:
            return await self.update_lead_v4(*args, **kwargs)
        else:
            return await self.update_lead_v2(*args, **kwargs)

    async def update_lead_v4(
        self,
        *,
        lead_id: int,
        price: Optional[int] = None,
        city_slug: Optional[str] = None,
        status_id: Optional[int] = None,
        status: str | None = None,
        property_id: Optional[int] = None,
        property_type: Optional[str] = None,
        booking_type_id: Optional[int] = None,
        booking_discount: Optional[int] = None,
        price_with_sales: Optional[int] = None,
        project_amocrm_name: Optional[str] = None,
        project_amocrm_enum: Optional[int] = None,
        project_amocrm_pipeline_id: Optional[int] = None,
        project_amocrm_responsible_user_id: Optional[int] = None,
        project_amocrm_organization: Optional[str] = None,
        meeting_date_sensei: Optional[datetime.timestamp] = None,
        meeting_date_zoom: Optional[datetime.timestamp] = None,
        meeting_date_next_contact: Optional[datetime.timestamp] = None,
        meeting_type_next_contact: Optional[str] = None,
        tags: list[AmoTag] | None = None,
        payment_type_enum: Optional[int] = None,
        tilda_offer_amo: dict | None = None,
        online_purchase_status: str | None = None,
        online_purchase_start_datetime: int | None = None,
        ddu_acceptance_datetime: int | None = None,
        ddu_upload_url: str | None = None,
        send_documents_datetime: int | None = None,
        online_purchase_id: str | None = None,
        is_mortgage_approved: bool | None = None,
        payment_method: AmoCRMPaymentMethod | None = None,
        booking_end: int | None = None,
        booking_price: int | None = None,
        is_agency_deal: bool | None = None,
        booking_expires_datetime: int | None = None,
    ):
        """
        https://www.amocrm.ru/developers/content/crm_platform/leads-api#leads-edit
        """
        route: str = f"/leads/{lead_id}"
        custom_fields = []

        if self.__is_strana_lk_2882_enable:
            if status_id is None:
                if status and city_slug:
                    # NOTE: цитата "по Москве предлагаю закрыть онлайн покупку, т.к там один объект остался
                    # и процессы пока старые в crm, как появятся объекты в Мск, то доработаем логику и
                    # откроем онлайн-покупку"
                    if status == "mortgage_apply" and city_slug == "msk":
                        raise ValueError("Онлайн-покупка для Москвы пока что недоступна.")
                    status_id: int = getattr(self, f"{self.lead_city_mapping[city_slug]}_status_ids")[status]

        # Город
        if city_slug is not None:
            custom_fields.append(
                dict(
                    field_id=self.city_field_id,
                    values=[self.city_field_values.get(city_slug, {})]
                )
            )

        # Проект
        if project_amocrm_name is not None:
            custom_fields.append(
                dict(
                    field_id=self.project_field_id,
                    values=[dict(value=project_amocrm_name, enum_id=project_amocrm_enum)],
                )
            )

        # Объект недвижимости
        if property_id is not None:
            custom_fields.append(
                dict(
                    field_id=self.property_field_id,
                    values=[dict(value=property_id)],
                )
            )

        # Тип объекта недвижимости
        if property_type is not None:
            custom_fields.append(
                dict(
                    field_id=self.property_type_field_id,
                    values=[dict(**self.property_type_field_values.get(property_type, {}))],
                )
            )

        # Тип бронирования
        if booking_type_id is not None:
            custom_fields.append(
                dict(
                    field_id=self.booking_type_field_id,
                    values=[dict(enum_id=booking_type_id)],
                )
            )

        # Размер скидки/акции
        if booking_discount is not None:
            custom_fields.append(
                dict(
                    field_id=self.booking_discounts_and_promotions,
                    values=[dict(value=int(booking_discount))],
                )
            )

        # Стоимость с учетом скидки
        if price_with_sales is not None:
            custom_fields.append(
                dict(
                    field_id=self.property_price_with_sale_field_id,
                    values=[dict(value=int(price_with_sales))]
                )
            )

        # Время встречи
        if meeting_date_sensei:
            custom_fields.append(
                dict(
                    field_id=self.meeting_date_sensei_field_id,
                    values=[dict(value=int(meeting_date_sensei))]
                )
            )
        if meeting_date_zoom:
            custom_fields.append(
                dict(
                    field_id=self.meeting_date_zoom_field_id,
                    values=[dict(value=int(meeting_date_zoom))]
                )
            )
        if meeting_date_next_contact:
            custom_fields.append(
                dict(
                    field_id=self.meeting_date_next_contact_field_id,
                    values=[dict(value=int(meeting_date_next_contact))]
                )
            )

        if meeting_type_next_contact:
            custom_fields.append(
                dict(
                    field_id=self.meeting_type_next_contact_field_id,
                    values=[self.meeting_types_next_contact_map.get(meeting_type_next_contact, {})]
                )
            )

        #  Тип оплаты (по матрице способов оплаты из амо)
        if payment_type_enum is not None:
            custom_fields.append(
                dict(
                    field_id=self.booking_payment_type_field_id,
                    values=[self.booking_payment_types_values.get(payment_type_enum, {})]
                )
            )

        if tilda_offer_amo:
            custom_fields.append(
                dict(
                    field_id=self.commercial_offer_field_id,
                    values=[dict(value=str(tilda_offer_amo).replace("'", '"').replace("None", "null"))]
                )
            )
        # Статус онлайн-покупки
        if online_purchase_status is not None:
            custom_fields.append(
                dict(
                    id=self.booking_online_purchase_status_field_id,
                    values=[self.online_purchase_status_map[online_purchase_status]],
                )
            )
        # Дата и время начала онлайн-покупки
        if online_purchase_start_datetime is not None:
            custom_fields.append(
                dict(
                    id=self.booking_online_purchase_start_datetime_field_id,
                    values=[dict(value=online_purchase_start_datetime)],
                )
            )
        # Дата и время согласования договора
        if ddu_acceptance_datetime is not None:
            custom_fields.append(
                dict(
                    id=self.booking_ddu_acceptance_datetime_field_id,
                    values=[dict(value=ddu_acceptance_datetime)],
                )
            )
        # Ипотека одобрена?
        if is_mortgage_approved is not None:
            custom_fields.append(
                dict(
                    id=self.booking_is_mortgage_approved_field_id,
                    values=[dict(value="да" if is_mortgage_approved else "нет")],
                )
            )
        # Форма для загрузки ДДУ
        if ddu_upload_url is not None:
            custom_fields.append(
                dict(id=self.booking_ddu_upload_url_field_id, values=[dict(value=ddu_upload_url)])
            )
        # Дата и время отправки документов на регистрацию
        if send_documents_datetime is not None:
            custom_fields.append(
                dict(
                    id=self.booking_send_documents_datetime_field_id,
                    values=[dict(value=send_documents_datetime)],
                )
            )
        # ID онлайн-покупки
        if online_purchase_id is not None:
            custom_fields.append(
                dict(
                    id=self.booking_online_purchase_id_field_id,
                    values=[dict(value=online_purchase_id)],
                )
            )

        if booking_end and booking_price:
            custom_fields: list[dict[str, Any]] = self._get_lead_payed_custom_fields(
                booking_end=booking_end, booking_price=booking_price
            )
        custom_fields = self._append_is_agency_deal(custom_fields, is_agency_deal)
        # Дата и время окончания бронирования
        if booking_expires_datetime:
            custom_fields.append(
                dict(
                    id=self.booking_expires_datetime_field_id,
                    values=[dict(value=booking_expires_datetime)],
                )
            )

        payload = dict(custom_fields_values=custom_fields)

        if price:
            payload.update(price=price)
        if status_id:
            payload.update(status_id=status_id)
        if project_amocrm_responsible_user_id:
            payload.update(responsible_user_id=int(project_amocrm_responsible_user_id))
        if project_amocrm_organization:
            payload.update(project_amocrm_organization=project_amocrm_organization)
        if project_amocrm_pipeline_id:
            payload.update(pipeline_id=int(project_amocrm_pipeline_id))
        if tags:
            payload.update(
                dict(
                    _embedded=AmoLeadEmbedded(
                        tags=tags,
                    ).dict(exclude_unset=True)
                )
            )

        self.logger.debug(f"Payload lead v4: {payload}")
        response: CommonResponse = await self._request_patch_v4(route=route, payload=payload)

        if self.__is_strana_lk_2882_enable:
            response_data = getattr(response, 'data', {})
            self.logger.debug(f"Lead Update v4 1:{response_data=}")
            try:
                leads: list[Any] = response_data.get("_embedded", {}).get("leads")
            except (ValidationError, AttributeError) as err:
                self.logger.debug(f"Lead Update v4 ERROR: {err=} {response_data=}")
                leads: list[Any] = []

            self.logger.debug(f"Lead Update v4 2:{leads=}")
            leads = [
                dict(id=lead_id),
            ]

            return leads

        else:
            if response:
                print(f'{response.data=}')
            return response.data if response else []

    async def update_leads_v4(
        self,
        *,
        lead_ids: list[int],
        price: Optional[int] = None,
        city_slug: Optional[str] = None,
        status_id: Optional[int] = None,
        property_id: Optional[int] = None,
        property_type: Optional[str] = None,
        booking_type_id: Optional[int] = None,
        booking_discount: Optional[int] = None,
        price_with_sales: Optional[int] = None,
        project_amocrm_name: Optional[str] = None,
        project_amocrm_enum: Optional[int] = None,
        project_amocrm_pipeline_id: Optional[int] = None,
        project_amocrm_responsible_user_id: Optional[int] = None,
        project_amocrm_organization: Optional[str] = None,
    ):
        route: str = f"/leads"
        custom_fields = []

        # Город
        if city_slug is not None:
            custom_fields.append(
                dict(
                    field_id=self.city_field_id,
                    values=[self.city_field_values.get(city_slug, {})]
                )
            )

        # Проект
        if project_amocrm_name is not None:
            custom_fields.append(
                dict(
                    field_id=self.project_field_id,
                    values=[dict(value=project_amocrm_name, enum_id=project_amocrm_enum)],
                )
            )

        # Объект недвижимости
        if property_id is not None:
            custom_fields.append(
                dict(
                    field_id=self.property_field_id,
                    values=[dict(value=property_id)],
                )
            )

        # Тип объекта недвижимости
        if property_type is not None:
            custom_fields.append(
                dict(
                    field_id=self.property_type_field_id,
                    values=[dict(**self.property_type_field_values.get(property_type, {}))],
                )
            )

        # Тип бронирования
        if booking_type_id is not None:
            custom_fields.append(
                dict(
                    field_id=self.booking_type_field_id,
                    values=[dict(enum_id=booking_type_id)],
                )
            )

        # Размер скидки/акции
        if booking_discount is not None:
            custom_fields.append(
                dict(
                    field_id=self.booking_discounts_and_promotions,
                    values=[dict(value=int(booking_discount))],
                )
            )

        # Стоимость с учетом скидки
        if price_with_sales is not None:
            custom_fields.append(
                dict(
                    field_id=self.property_price_with_sale_field_id,
                    values=[dict(value=int(price_with_sales))]
                )
            )

        payload = []
        for lead_id in lead_ids:
            lead_payload = dict(
                id=lead_id,
                custom_fields_values=custom_fields,
            )
            if price:
                lead_payload.update(price=price)
            if status_id:
                lead_payload.update(status_id=status_id)
            if project_amocrm_responsible_user_id:
                lead_payload.update(responsible_user_id=int(project_amocrm_responsible_user_id))
            if project_amocrm_organization:
                lead_payload.update(project_amocrm_organization=project_amocrm_organization)
            if project_amocrm_pipeline_id:
                lead_payload.update(pipeline_id=int(project_amocrm_pipeline_id))
            payload.append(lead_payload)

        self.logger.debug(f"Payload leads v4: {payload}")
        response: CommonResponse = await self._request_patch_v4(route=route, payload=payload)

        return response.data if response else []

    # deprecated
    async def update_lead_v2(
        self,
        *,
        lead_id: int,
        status: Optional[str] = None,
        status_id: Optional[int] = None,
        company: Optional[int] = None,
        city_slug: Optional[str] = None,
        tags: Optional[list[str]] = None,
        booking_end: Optional[int] = None,
        booking_price: Optional[int] = None,
        booking_expires_datetime: Optional[int] = None,
        contacts: Optional[list[int]] = None,
        online_purchase_status: Optional[str] = None,
        online_purchase_start_datetime: Optional[int] = None,
        is_mortgage_approved: Optional[bool] = None,
        payment_method: Optional[AmoCRMPaymentMethod] = None,
        ddu_upload_url: Optional[str] = None,
        send_documents_datetime: Optional[int] = None,
        online_purchase_id: Optional[str] = None,
        ddu_acceptance_datetime: Optional[int] = None,
        property_id: Optional[int] = None,
        property_type: Optional[str] = None,
        booking_type_id: Optional[int] = None,
        is_agency_deal: Optional[bool] = None,
        payment_type_enum: Optional[int] = None,
    ) -> list[Any]:
        """
        Lead mutation
        """
        route: str = "/leads"
        payload: dict[str, Any] = dict(
            update=[dict(id=lead_id, updated_at=int(datetime.now(tz=UTC).timestamp()))]
        )
        if tags:
            payload["update"][0]["tags"]: list[str] = tags
        if company:
            payload["update"][0]["company_id"]: int = company
        if contacts:
            payload["update"][0]["contacts_id"]: list[int] = contacts
        if status_id:
            payload["update"][0]["status_id"] = status_id
        elif status and city_slug:
            # NOTE: цитата "по Москве предлагаю закрыть онлайн покупку, т.к там один объект остался
            # и процессы пока старые в crm, как появятся объекты в Мск, то доработаем логику и
            # откроем онлайн-покупку"
            if status == "mortgage_apply" and city_slug == "msk":
                raise ValueError("Онлайн-покупка для Москвы пока что недоступна.")

            payload["update"][0]["status_id"]: int = getattr(
                self, f"{self.lead_city_mapping[city_slug]}_status_ids"
            )[status]

        custom_fields: list[Any] = []
        if booking_end and booking_price:
            custom_fields: list[dict[str, Any]] = self._get_lead_payed_custom_fields(
                booking_end=booking_end, booking_price=booking_price
            )

        # Объект недвижимости
        if property_id:
            custom_fields.append(
                dict(
                    id=self.property_field_id,
                    values=[dict(value=property_id)],
                )
            )

        # Тип объекта недвижимости
        if property_type:
            custom_fields.append(
                dict(
                    id=self.property_type_field_id,
                    values=[dict(**self.property_type_field_values.get(property_type, {}))],
                )
            )

        # Тип бронирования
        if booking_type_id:
            custom_fields.append(
                dict(
                    id=self.booking_type_field_id,
                    values=[dict(enum_id=booking_type_id)],
                )
            )

        # Дата и время окончания бронирования
        if booking_expires_datetime:
            custom_fields.append(
                dict(
                    id=self.booking_expires_datetime_field_id,
                    values=[dict(value=booking_expires_datetime)],
                )
            )

        # Статус онлайн-покупки
        if online_purchase_status is not None:
            custom_fields.append(
                dict(
                    id=self.booking_online_purchase_status_field_id,
                    values=[self.online_purchase_status_map[online_purchase_status]],
                )
            )
        # Дата и время начала онлайн-покупки
        if online_purchase_start_datetime is not None:
            custom_fields.append(
                dict(
                    id=self.booking_online_purchase_start_datetime_field_id,
                    values=[dict(value=online_purchase_start_datetime)],
                )
            )

        #  Тип оплаты (по матрице способов оплаты из амо)
        if payment_type_enum is not None:
            custom_fields.append(
                dict(
                    field_id=self.booking_payment_type_field_id,
                    values=[self.booking_payment_types_values.get(payment_type_enum, {})]
                )
            )

        custom_fields = self._append_is_agency_deal(custom_fields, is_agency_deal)

        # Ипотека одобрена?
        if is_mortgage_approved is not None:
            custom_fields.append(
                dict(
                    id=self.booking_is_mortgage_approved_field_id,
                    values=[dict(value="да" if is_mortgage_approved else "нет")],
                )
            )
        # Форма для загрузки ДДУ
        if ddu_upload_url is not None:
            custom_fields.append(
                dict(id=self.booking_ddu_upload_url_field_id, values=[dict(value=ddu_upload_url)])
            )
        # Дата и время отправки документов на регистрацию
        if send_documents_datetime is not None:
            custom_fields.append(
                dict(
                    id=self.booking_send_documents_datetime_field_id,
                    values=[dict(value=send_documents_datetime)],
                )
            )
        # ID онлайн-покупки
        if online_purchase_id is not None:
            custom_fields.append(
                dict(
                    id=self.booking_online_purchase_id_field_id,
                    values=[dict(value=online_purchase_id)],
                )
            )
        # Дата и время согласования договора
        if ddu_acceptance_datetime is not None:
            custom_fields.append(
                dict(
                    id=self.booking_ddu_acceptance_datetime_field_id,
                    values=[dict(value=ddu_acceptance_datetime)],
                )
            )

        if custom_fields:
            payload["update"][0]["custom_fields"]: list[Any] = custom_fields

        response: CommonResponse = await self._request_post(route=route, payload=payload)

        if response.data:
            data: list[Any] = response.data["_embedded"]["items"]
        else:
            data: list[Any] = []
        return data

    def _append_is_agency_deal(self, custom_fields, is_agency_deal):
        if is_agency_deal is not None:
            custom_fields.append(
                dict(
                    id=self.booking_is_agency_deal_field_id,
                    values=[dict(value="да" if is_agency_deal else "нет")],
                )
            )

        return custom_fields

    # deprecated
    async def update_showtime(self, lead_id: int) -> list[Any]:
        """
        Showtime mutation
        """

        route: str = "/leads"
        payload: dict[str, Any] = dict(
            update=[
                dict(
                    id=lead_id,
                    status_id=self.showtime_process_status_id,
                    updated_at=int(datetime.now(tz=UTC).timestamp()),
                )
            ]
        )
        response: CommonResponse = await self._request_post(route=route, payload=payload)
        if response.data:
            data: list[Any] = response.data["_embedded"]["items"]
        else:
            data: list[Any] = []
        return data
    
    async def update_showtime_v4(self, lead_id: int) -> list[Any]:
        """
        Showtime mutation v_4
        """

        route: str = "/leads"
        payload: dict[str, Any] = dict(
            update=[
                dict(
                    id=lead_id,
                    status_id=self.showtime_process_status_id,
                    updated_at=int(datetime.now(tz=UTC).timestamp()),
                )
            ]
        )
        response: CommonResponse = await self._request_post_v4(route=route, payload=payload)
        return await self._parse_leads_data_no_exception(
            response=response,
            method_name='cabinet/amocrm/update_showtime_v4',
            payload=payload,
        )

    # deprecated
    async def register_lead(self, user_amocrm_id: int) -> list[Any]:
        """
        Register lead creation
        """

        route: str = "/leads"
        payload: dict[str, Any] = dict(
            add=[
                dict(
                    name=self.default_lead_name,
                    created_at=int(datetime.now(tz=UTC).timestamp()),
                    updated_at=int(datetime.now(tz=UTC).timestamp()),
                    status_id=self.start_status_id,
                    pipeline_id=self.start_pipeline_id,
                    tags=self.start_tags,
                    contacts_id=[user_amocrm_id],
                    responsible_user_id=self.start_responsible_user,
                )
            ]
        )
        response: CommonResponse = await self._request_post(route=route, payload=payload)
        if response.data:
            data: list[Any] = response.data["_embedded"]["items"]
        else:
            data: list[Any] = []
        return data

    async def register_lead_v4(self, user_amocrm_id: int) -> list[Any]:
        """
        Register lead creation v_4
        """

        route: str = "/leads"
        tags: list[AmoTag] = [AmoTag(name=tag) for tag in self.start_tags]
        contacts: list[AmoLeadContact] = [AmoLeadContact(id=user_amocrm_id, is_main=True)]
        payload: AmoLead = AmoLead(
            name=self.default_lead_name,
            created_at=int(datetime.now(tz=UTC).timestamp()),
            updated_at=int(datetime.now(tz=UTC).timestamp()),
            status_id=self.start_status_id,
            pipeline_id=self.start_pipeline_id,
            responsible_user_id=self.start_responsible_user,
            _embedded=AmoLeadEmbedded(
                tags=tags,
                contacts=contacts,
            )
        )

        response: CommonResponse = await self._request_post_v4(route=route, payload=[payload.dict(exclude_unset=True)])

        return await self._parse_leads_data_no_exception(
            response=response,
            method_name='cabinet/amocrm/register_lead_v4',
            payload=payload,
        )

    async def get_leads_pipelines(self) -> list[Any]:
        route: str = '/leads/pipelines'
        response: CommonResponse = await self._request_get_v4(route=route, query={})
        data = jmespath.search('_embedded.pipelines', response.data)
        return data or []

    @staticmethod
    def get_lead_substage(lead_status_id) -> Optional[str]:
        """
        Получение отображаемого в ЛК статуса сделки исходя из статуса в AmoCRM.
        """

        cls = AmoCRMLeads
        if lead_status_id in cls.tmn_import_status_ids:
            return cls.tmn_substages.get(lead_status_id)
        elif lead_status_id in cls.msk_import_status_ids:
            return cls.msk_substages.get(lead_status_id)
        elif lead_status_id in cls.spb_import_status_ids:
            return cls.spb_substages.get(lead_status_id)
        elif lead_status_id in cls.ekb_import_status_ids:
            return cls.ekb_substages.get(lead_status_id)
        elif lead_status_id in cls.test_import_status_ids:
            return cls.test_case_substages.get(lead_status_id)
        elif lead_status_id in cls.call_center_import_status_ids:
            return cls.call_center_substages.get(lead_status_id)
        return None

    def _get_lead_default_custom_fields(
        self,
        city_slug: str,
        property_id: Optional[int],
        property_type: Optional[str],
        project_amocrm_name: Optional[str],
        project_amocrm_enum: Optional[int],
        project_amocrm_organization: Optional[str],
        booking_type_id: Optional[int],
        is_agency_deal: Optional[bool],
        payment_type_enum: Optional[int] = None,
    ) -> list[AmoCustomField]:
        """
        get lead default custom fields
        """

        custom_fields: list[AmoCustomField] = [
            AmoCustomField(field_id=self.city_field_id, values=[
                AmoCustomFieldValue(**self.city_field_values.get(city_slug, {}))
            ]),
            AmoCustomField(field_id=self.booking_start_field_id, values=[
                AmoCustomFieldValue(value=int(datetime.now(tz=UTC).timestamp()))
            ]),
        ]
        if property_id:
            custom_fields.append(AmoCustomField(field_id=self.property_field_id, values=[
                AmoCustomFieldValue(value=property_id)
            ]))
        if property_type:
            custom_fields.append(AmoCustomField(field_id=self.property_type_field_id, values=[
                AmoCustomFieldValue(**self.property_type_field_values.get(property_type, {}))
            ]))
        if project_amocrm_name and project_amocrm_enum:
            custom_fields.append(AmoCustomField(field_id=self.project_field_id, values=[
                AmoCustomFieldValue(value=project_amocrm_name, enum_id=project_amocrm_enum)
            ]))
        if project_amocrm_organization:
            custom_fields.append(AmoCustomField(field_id=self.organization_field_id, values=[
                AmoCustomFieldValue(value=project_amocrm_organization)
            ]))
        if booking_type_id:
            custom_fields.append(AmoCustomField(field_id=self.booking_type_field_id, values=[
                AmoCustomFieldValue(enum_id=booking_type_id)
            ]))
        if is_agency_deal is not None:
            custom_fields.append(AmoCustomField(field_id=self.booking_is_agency_deal_field_id, values=[
                AmoCustomFieldValue(value="Да" if is_agency_deal else "Нет")
            ]))
        if payment_type_enum is not None:
            custom_fields.append(
                AmoCustomField(field_id=self.booking_payment_type_field_id, values=[
                    AmoCustomFieldValue(**self.booking_payment_types_values.get(payment_type_enum, {}))
                ])
            )

        return custom_fields

    def _get_showtime_custom_fields(
        self,
        city_slug: str,
        visit: datetime,
        property_type: str,
        project_amocrm_name: str,
        project_amocrm_enum: int,
    ) -> list[AmoCustomField]:
        """
        get showtime custom fields
        """

        custom_fields: list[AmoCustomField] = [
            AmoCustomField(field_id=self.city_field_id, values=[
                AmoCustomFieldValue(**self.city_field_values.get(city_slug, {}))
            ]),
            AmoCustomField(field_id=self.project_field_id, values=[
                AmoCustomFieldValue(value=project_amocrm_name, enum_id=project_amocrm_enum)
            ]),
            AmoCustomField(field_id=self.property_type_field_id, values=[
                AmoCustomFieldValue(**self.property_type_field_values.get(property_type, {}))
            ]),
            AmoCustomField(field_id=self.showtime_datetime_field_id, values=[
                AmoCustomFieldValue(value=int(visit.timestamp()))
            ]),
        ]
        return custom_fields

    def _get_lead_payed_custom_fields(
        self, booking_end: int, booking_price: int
    ) -> list[dict[str, Any]]:
        """
        get lead payed custom field
        """

        booking_end: int = int((timedelta(days=booking_end) + datetime.now(tz=UTC)).timestamp())
        custom_fields: list[dict[str, Any]] = [
            dict(id=self.booking_end_field_id, values=[dict(value=booking_end)]),
            dict(id=self.booking_price_field_id, values=[dict(value=booking_price)]),
            dict(id=self.booking_payment_status_field_id, values=[dict(value="Да")]),
            dict(id=self.booking_payment_field_id, values=[dict(value="Да")]),
            dict(id=self.booking_discount_price_field_id, values=[dict(value=booking_price)]),
        ]
        return custom_fields

    async def _parse_leads_data(self, response: CommonResponse, method_name: str, payload) -> list[AmoLead]:
        """
        parse_leads_data
        """
        try:
            items: list[Any] = getattr(response, "data", {}).get("_embedded", {}).get("leads")
            return parse_obj_as(list[AmoLead], items)
        except (ValidationError, AttributeError) as err:
            message = (f"{method_name}: Status {response.status}: "
                       f"Пришли неверные данные: {response.data}"
                       f"Exception: {err}")
            self.logger.warning(message)
            raise AmocrmHookError(reason=message) from err

    async def _parse_leads_data_no_exception(self, response: CommonResponse, method_name: str, payload) -> list:
        """
        parse_leads_data_no_exception
        """
        try:
            leads: list[Any] = getattr(response, "data", {}).get("_embedded", {}).get("leads")
            return leads
        except (ValidationError, AttributeError) as err:
            message = (f"{method_name}: Status {response.status}: "
                       f"Пришли неверные данные: {response.data}"
                       f"Exception: {err}")
            self.logger.warning(message)
            sentry_ctx: dict[str, Any] = dict(
                response_status=response.status,
                response_data=response.data,
                payload=payload,
                method_name=method_name,
                err=err,
            )
            await send_sentry_log(
                tag="AMO",
                message=f"{method_name} Неожидаемый ответ от AMO",
                context=sentry_ctx,
            )
            return []

    async def lead_link_entities(
        self,
        lead_id: int,
        entities: list[Entity],
    ) -> None:
        """
        Привязка сущностей к сделке
        """
        route: str = f"/leads/{lead_id}/link"
        payload = []
        for entity in entities:
            payload.extend([
                dict(
                    to_entity_id=entity_id,
                    to_entity_type=entity.type,
                ) for entity_id in entity.ids
            ])

        await self._request_post_v4(route=route, payload=payload)

    async def leads_link_entities(
        self,
        lead_ids: list[int],
        entities: list[Entity],
    ) -> None:
        """
        Привязка сущностей к нескольким сделкам
        """
        route: str = f"/leads/link"
        payload = []
        for lead_id in lead_ids:
            for entity in entities:
                payload.extend([
                    dict(
                        entity_id=lead_id,
                        to_entity_id=entity_id,
                        to_entity_type=entity.type,
                    ) for entity_id in entity.ids
                ])

        await self._request_post_v4(route=route, payload=payload)

    async def lead_unlink_entities(
        self,
        lead_id: int,
        entities: list[Entity],
    ) -> None:
        """
        Отвязка сущностей от сделки
        """
        route: str = f"/leads/{lead_id}/unlink"
        payload = []
        for entity in entities:
            payload.extend([
                dict(
                    to_entity_id=entity_id,
                    to_entity_type=entity.type,
                ) for entity_id in entity.ids
            ])

        await self._request_post_v4(route=route, payload=payload)

    async def leads_unlink_entities(
        self,
        lead_ids: list[int],
        entities: list[Entity],
    ) -> None:
        """
        Отвязка сущностей от нескольких сделок
        """
        route: str = f"/leads/unlink"
        payload = []
        for lead_id in lead_ids:
            for entity in entities:
                payload.extend([
                    dict(
                        entity_id=lead_id,
                        to_entity_id=entity_id,
                        to_entity_type=entity.type,
                    ) for entity_id in entity.ids
                ])

        await self._request_post_v4(route=route, payload=payload)

    @property
    def __is_strana_lk_2882_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_2882)
