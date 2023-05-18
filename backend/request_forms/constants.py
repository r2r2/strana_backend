from django.db.models import TextChoices


class RequestType(TextChoices):
    VACANCY = "vacancy", "Отклик на вакансию"
    SALE = "sale", "Заявка на продажу участка"
    CALLBACK = "callback", "Заявка на обратный звонок"
    RESERVATION = "reservation", "Заявка на бронирование"
    EXCURSION = "excursion", "Запись на экскурсию"
    DIRECTOR = "director", "Запрос на связь с директором"
    PURCHASE = "purchase", "Заявка на помощь с оформлением покупки"
    AGENT = "agent", "Заявка агентств"
    CONTRACTOR = "Contractor", "Заявки для подрядчиков"
    CUSTOM = "custom", "Кастомная заявка"
    COMMERCIAL_RENT = "commercial_rent", "Заявка на аренду коммерческого помещения"
    MEDIA = "media", "Заявка для СМИ"
    REALTY_UPDATE = "realty_update", "Обновление недвижимости"
    LANDING = "lading", "Заявка с лендинга"
    ANTI_CORRUPTION = "anti_corruption", "Заявка о противодействии коррупции"
    TEASER = "teaser", "Заявка со слайда главной страницы (тизера)"
    NEWS = "news", "Заявка со страницы новости"
    OFFICE = "office", "Заявка на встречу в офисе"
    LOT_CARD = "lot_card", "Заявка с карточки лота"
    FLAT_LISTING = "flat_listing", "Заявка в листинге квартир"
    START_SALE = "start_sale", "Заявка на уведомление о старте продаж"
    MALLTEAM = "mallteam", "Заявка с формы MallTeam"
    COMMERCIAL_KOTELNIKI = "comm_kotelniki", "Заявка коммерции Котельники"
    SHOW = "show", "Заявка записи на показ"


class ProjectTimerRequestType(TextChoices):
    CALLBACK = "callback", "Заявка на обратный звонок"
    EXCURSION = "excursion", "Запись на экскурсию"


class TimeIntervalType(TextChoices):
    ANY = "any", "Любое"
    F9T11 = "9-11", "9:00-11:00"
    F11T13 = "11-13", "11:00-13:00"
    F13T15 = "13-15", "13:00-15:00"
    F15T17 = "15-17", "15:00-17:00"
    F17T19 = "17-19", "17:00-19:00"
