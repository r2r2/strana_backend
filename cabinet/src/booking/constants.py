from enum import IntEnum, StrEnum
from typing import Any, NamedTuple, Optional

from common import mixins
from common.amocrm.constants import BaseLeadSalesStatuses


class GetDocStatus(IntEnum):
    """
    Id статуса для сделки создания документа в гетдоке
    """

    NEW = 56786437


class BookingStages(mixins.Choices):
    """
    Этапы бронирования
    """

    START: str = "start", "Первичный контакт"
    BOOKING: str = "booking", "Онлайн-бронирование"
    DDU_PROCESS: str = "ddu_process", "Оформление ДДУ"
    DDU_SIGNING: str = "ddu_signing", "Подписание ДДУ"
    DDU_REGISTER: str = "ddu_register", "ДДУ на регистрации"
    DDU_FINISHED: str = "ddu_finished", "Успешно реализовано"
    DDU_UNREGISTERED: str = "ddu_unregistered", "ДДУ не зарегистрирован"


class BookingSubstages(mixins.Choices, BaseLeadSalesStatuses):
    """
    Подэтапы бронирования
    """

    START: str = "start", "Первичный контакт"
    ASSIGN_AGENT = "assign_agent", "Фиксация клиента за агентом"
    MAKE_APPOINTMENT = "make_appointment", "Назначить встречу"
    MEETING = "meeting", "Встреча назначена"
    MEETING_IN_PROGRESS = "meeting_in_progress", "Идёт встреча"
    MAKE_DECISION = 'make_decision', "Принимают решение"
    RE_MEETING = "re_meeting", "Повторная встреча"

    BOOKING: str = "booking", "Бронь"
    PAID_BOOKING: str = "paid_booking", "Платная бронь"
    MORTGAGE_LEAD: str = "mortgage_lead", "Заявка на ипотеку"
    APPLY_FOR_A_MORTGAGE: str = "apply_for_a_mortgage", "Подать на ипотеку"
    MORTGAGE_FILED: str = "mortgage_filed", "Ипотека подана"
    MORTGAGE_DONE: str = "mortgage_done", "Ипотека одобрена"

    DDU_PROCESS: str = "ddu_process", "Оформление ДДУ"
    CONFIRMATION: str = "confirmation", "Согласование"

    DDU_SIGNING: str = "ddu_signing", "Подписание ДДУ"

    DDU_REGISTER: str = "ddu_register", "ДДУ на регистрации"

    REALIZED: str = "realized", "Успешно реализовано"
    MONEY_PROCESS: str = "money_process", "Зачисление денег"

    UNREALIZED: str = "unrealized", "Закрыто и не реализовано"
    TERMINATION: str = "termination", "Расторжение"


class OnlinePurchaseStatuses(mixins.Choices):
    """
    Статусы онлайн-покупки
    """

    STARTED: str = "started", "Приступил к онлайн-покупке"
    DOCS_SENT: str = "docs_sent", "Отправил документы на регистрацию"
    DDU_ACCEPTED: str = "ddu_accepted", "Согласовал договор"
    DDU_REGISTERED: str = "ddu_registered", "Договор зарегистрирован"


class BookingCreatedSources(mixins.Choices):
    """
    Источники создания бронирования
    """
    AMOCRM: str = "amocrm", "Импортирован из AMOCRM",
    LK: str = "lk_booking", "Бронирование через личный кабинет"
    LK_ASSIGN: str = "lk_booking_assign", "Закреплен в ЛК Брокера"
    FAST_BOOKING: str = "fast_booking", "Быстрое бронирование"


class OnlinePurchaseSteps(mixins.Choices):
    """
    Шаги онлайн-покупки
    """

    #: Клиент должен принять оферту
    ONLINE_PURCHASE_START: str = "online_purchase_start", "Начало онлайн покупки"

    #: Клиент должен принять оферту
    PAYMENT_METHOD_SELECT: str = "payment_method_select", "Выбор способа покупки"

    #: Ожидаем, когда в AmoCRM проверят данные (данные для связи с банком или заявку на ипотеку,
    #: если клиент их указывал)
    AMOCRM_AGENT_DATA_VALIDATION: str = (
        "amocrm_agent_data_validation",
        "Ожидайте, введённые данные на проверке",
    )

    #: Клиент должен заполнить ДДУ
    DDU_CREATE: str = "ddu_create", "Оформление договора"

    #: Ожидаем загрузку ДДУ от юриста. Также тут клиент может изменять ДДУ
    AMOCRM_DDU_UPLOADING_BY_LAWYER: str = (
        "amocrm_ddu_uploading_by_lawyer",
        "Ожидание загрузки ДДУ юристом",
    )

    #: Клиент должен нажать на кнопку "Ознакомлен"
    DDU_ACCEPT: str = "ddu_accept", "Согласование договора"

    #: Клиент должен загрузить эскроу-счёт
    ESCROW_UPLOAD: str = "escrow_upload", "Загрузка эскроу-счёта"

    #: Ожидаем, пока в AmoCRM назначат дату подписания договора
    AMOCRM_SIGNING_DATE: str = "amocrm_signing_date", "Ожидание назначения даты подписания договора"

    #: Ожидаем, пока в AmoCRM отметят, что договор подписан
    AMOCRM_SIGNING: str = "amocrm_signing", "Ожидание подписания договора"

    #: Договор был подписан. Конец
    FINISHED: str = "finished", "Зарегистрировано"


class PaymentStatuses(mixins.Choices):
    """
    Статус платежа
    """

    CREATED: int = 0, "Создано"
    PENDING: int = 1, "Отправлено"
    SUCCEEDED: int = 2, "Успешно"
    FAILED: int = 3, "Неуспешно"
    REFUNDED: int = 4, "Возмещено"
    DECLINED: int = 6, "Отклонено"


class BookingPayKind(StrEnum):
    """
    Состояние процесса оплаты.
    """
    SUCCESS: str = "success"
    FAIL: str = "fail"


class PaymentView(mixins.Choices):
    """
    Отображение оплаты
    """

    DESKTOP: str = "DESKTOP", "Полный экран"
    MOBILE: str = "MOBILE", "Адаптив"


class BookingStagesMapping(object):
    """
    Соотношение этапов с подэтапами
    """

    MAPPING: dict[str, Any] = {
        BookingSubstages.START: BookingStages.START,
        BookingSubstages.ASSIGN_AGENT: BookingStages.START,
        BookingSubstages.MAKE_APPOINTMENT: BookingStages.START,
        BookingSubstages.MEETING: BookingStages.START,
        BookingSubstages.MEETING_IN_PROGRESS: BookingStages.START,
        BookingSubstages.MAKE_DECISION: BookingStages.START,
        BookingSubstages.RE_MEETING: BookingStages.START,
        BookingSubstages.BOOKING: BookingStages.BOOKING,
        BookingSubstages.PAID_BOOKING: BookingStages.BOOKING,
        BookingSubstages.MORTGAGE_LEAD: BookingStages.BOOKING,
        BookingSubstages.APPLY_FOR_A_MORTGAGE: BookingStages.BOOKING,
        BookingSubstages.MORTGAGE_FILED: BookingStages.BOOKING,
        BookingSubstages.MORTGAGE_DONE: BookingStages.BOOKING,
        BookingSubstages.DDU_PROCESS: BookingStages.DDU_PROCESS,
        BookingSubstages.CONFIRMATION: BookingStages.DDU_PROCESS,
        BookingSubstages.DDU_SIGNING: BookingStages.DDU_SIGNING,
        BookingSubstages.DDU_REGISTER: BookingStages.DDU_REGISTER,
        BookingSubstages.REALIZED: BookingStages.DDU_FINISHED,
        BookingSubstages.MONEY_PROCESS: BookingStages.DDU_FINISHED,
        BookingSubstages.UNREALIZED: BookingStages.DDU_UNREGISTERED,
        BookingSubstages.TERMINATION: BookingStages.DDU_UNREGISTERED,
    }

    def __getitem__(self, item: str) -> str:
        return self.MAPPING.get(item)


class PaymentMethods(mixins.Choices):
    """
    Способы покупки
    todo: payment_method
    """

    CASH: str = "cash", "Наличные"
    MORTGAGE: str = "mortgage", "Ипотека"
    INSTALLMENT_PLAN: str = "installment_plan", "Рассрочка"


class MaritalStatus(mixins.Choices):
    """
    Семейное положение
    """

    SINGLE: str = "single", "Не в браке"
    MARRIED: str = "married", "В браке"


class RelationStatus(mixins.Choices):
    """
    Кем приходится
    """

    WIFE: str = "wife", "Супруга"
    HUSBAND: str = "husband", "Супруг"
    CHILD: str = "child", "Ребёнок"
    OTHER: str = "other", "Иное"


class UploadPath(mixins.Choices):
    """
    Пути загрузок
    """

    DDU_FILES: str = "b/f/d", "Файлы участников ДДУ"
    DDU_PARTICIPANTS: str = "b/f/p", "Файлы участников ДДУ"
    BOOKING_FILES: str = "b/f/b", "Файлы бронирований"


class BookingFileType(mixins.Choices):
    """
    Тип файла для бронирования
    """

    DDU_BY_LAWYER: str = "ddu_by_lawyer", "ДДУ, загруженный"
    ESCROW: str = "escrow", "Документ об открытии эскроу-счёта"


class DDUFileType(mixins.Choices):
    """
    Тип файла ДДУ
    """

    MATERNAL_CAPITAL_CERTIFICATE_IMAGE: str = (
        "maternal_capital_certificate_image",
        "Сертификат из ПФР об остатке денежных средств на счете",
    )
    MATERNAL_CAPITAL_STATEMENT_IMAGE: str = (
        "maternal_capital_statement_image",
        "Справка из ПФР об остатке денежных средств на счете",
    )
    HOUSING_CERTIFICATE_IMAGE: str = (
        "housing_certificate_image",
        "Сертификат, который дают клиенту в организации, выдавшей сертификат",
    )
    HOUSING_CERTIFICATE_MEMO_IMAGE: str = (
        "housing_certificate_memo_image",
        "Памятка, которую дают клиенту в организации, выдавшей сертификат",
    )


class DDUParticipantFileType(mixins.Choices):
    """
    Тип файла участника ДДУ
    """

    BIRTH_CERTIFICATE_IMAGE: str = "birth_certificate_image", "Свидетельство о рождении"
    REGISTRATION_IMAGE: str = "registration_image", "Страница действующей прописки"
    INN_IMAGE: str = "inn_image", "ИНН"
    SNILS_IMAGE: str = "snils_image", "СНИЛС"


FORBIDDEN_FOR_BOOKING_PROPERTY_PARAMS: list[str] = ["preferential_mortgage", "maternal_capital"]

PAYMENT_PROPERTY_NAME = "Услуга по онлайн бронированию объекта недвижимости {}"

DDU_ALLOWED_FILE_EXTENSIONS = {'application/pdf', 'image/jpeg', 'image/png', 'image/tiff'}


class BookingTypeNamedTuple(NamedTuple):
    price: int
    amocrm_id: Optional[int] = None


class BookingTagStyle(mixins.Choices):
    """
    Стили тегов
    """
    PRIMARY: str = "primary", "Основной"
    SECONDARY: str = "secondary", "Второстепенный"
    DANGER: str = "danger", "Опасный"
    WARNING: str = "warning", "Предупреждение"
    INFO: str = "info", "Информация"
    LIGHT: str = "light", "Светлый"
    DARK: str = "dark", "Темный"
    LINK: str = "link", "Ссылка"

    DEFAULT: str = "default", "По умолчанию"
    SUCCESS: str = "success", "Успешно"
    WHITE: str = "white", "Белый"
    TRANSPARENT: str = "transparent", "Прозрачный"


class BookingFixationNotificationType(mixins.Choices):
    """
    Типы событий уведомления об окончании фиксации.
    """
    EXTEND: str = "extend", "Продление фиксации"
    FINISH: str = "finish", "Окончании фиксации"
