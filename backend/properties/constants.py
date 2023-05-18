from django.db.models import IntegerChoices, TextChoices


class PropertyStatus(IntegerChoices):
    FREE = 0, "Свободен"
    SOLD = 1, "Продан"
    BOOKED = 2, "Забронирован"
    UNAVAILABLE = 3, "Не для продажи"


class PropertyType(TextChoices):
    FLAT = "flat", "Квартира"
    PARKING = "parking", "Парковочное место"
    COMMERCIAL = "commercial", "Коммерческое помещение"
    PANTRY = "pantry", "Кладовка"
    COMMERCIAL_APARTMENT = "commercial_apartment", "Аппартаменты коммерции"


class ApplicantType(TextChoices):
    REALTOR = "realtor", "Риелтор"
    PERSON = "person", "Частное лицо"


class DiscountUnit(TextChoices):
    PERCENT = "PERCENT", "Проценты"
    VALUE = "VALUE", "Рубли"


FLAT_TYPES: list = [PropertyType.FLAT, PropertyType.COMMERCIAL_APARTMENT]
COMMERCIAL_TYPES: list = [PropertyType.COMMERCIAL, PropertyType.COMMERCIAL_APARTMENT]
PARKING_PANTRY_TYPES: list = [PropertyType.PARKING, PropertyType.PANTRY]


class SimilarPropertiesTab(TextChoices):
    LESS_PRICE = "less_price", "Дешевле"
    LARGER_AREA = "larger_area", "Больше площадь"
    WITH_FURNISH = "with_furnish", "С отделкой"


class PropertyCardKind(TextChoices):
    FLAT = "flat", "Квартира"
    PARKING = "parking", "Парковочное место"
    COMMERCIAL = "commercial", "Коммерческое помещение"
    PANTRY = "pantry", "Кладовка"
    ANOTHER = "another", "Другое"


class FeatureType(TextChoices):
    FACING = "facing", "Отделка"
    PARKING = "has_parking", "Паркинг"
    ACTION_PARKING = "has_action_parking", "Паркинг по спец. цене"
    TERRACE = "has_terrace", "Терраса"
    VIEW = "has_view", "Видовые"
    PANORAMIC = "has_panoramic_windows", "Панорамные окна"
    TWO_SIDES = "has_two_sides_windows", "Окна на 2 стороны"
    DUPLEX = "is_duplex", "Двухуровневая"
    HIGH_CEILING = "has_high_ceiling", "Высокий потолок"
    INSTALLMENT = "installment", "Рассрочка"
    FRONTAGE = "frontage", "Палисадник"
    PREF_MORTGAGE = "preferential_mortgage", "Льготная ипотека"
    PREF_MORTGAGE_4 = "preferential_mortgage4", "Льготная ипотека 4.95%"
    HAS_TENANT = "has_tenant", "С арендатором"
    ACTION = "action", "Акция"
    FAVORITE_RATE = "favorable_rate", "Выгодная ставка"
    COMPLETED = "completed", "Завершенная"
    CORNER_WINDOWS = "corner_windows", "Угловые окна"
    MATERNAL_CAPITAL = "maternal_capital", "Материнский капитал"
    HAS_SEPARATE_ENTRANCE = "has_separate_entrance", "Отдельная входная группа"
    HAS_TWO_ENTRANCES = "has_two_entrances", "Два входа"
    HAS_STAINED_GLASS = "has_stained_glass", "Витражное остекление"
    HAS_FUNCTIONAL_LAYOUT = "has_functional_layout", "Функциональная планировка"
    HAS_PLACE_FOR_ADS = "has_place_for_ads", "Место под рекл. вывеску"
    HAS_CEILING_THREE_METERS = "has_ceiling_three_meters", "Потолок 3-3,6м"
    HAS_WATER_SUPPLY = "has_water_supply", "Горячее и холодное водоснабжение"
    HAS_DOT_TWO_KILOWATTS = "has_dot_two_kilowatts", "Эл. мощность 0,2 кВт/м2"
    HAS_OWN_VENTILATION = "has_own_ventilation", "Собственная вент. шахта"
    HAS_BALCONY_OR_LOGGIA = "has_balcony_or_loggia", "Есть балкон или лоджия"
    VIEW_CATHEDRAL = "view_cathedral", "Вид на Исаакиевский собор"
    VIEW_GULF = "view_gulf", "Вид на Финский залив"
    VIEW_RIVER = "view_river", "Вид на реку"
    VIEW_PARK = "view_park", "Вид на парк Екатерингоф"
    VIEW_TEMPLE = "view_temple", "Вид на храм"
    VIEW_SQUARE = "view_square", "Вид на сквер"
    VIEW_CENTER = "view_center", "Вид на центр"
    DEVELOPMENT_INFRASTRUCTURE = "developed_infrastructure", "Развитая инфраструктура"
    FIRST_LINE = "first_line", "Первая линия"
    RENOVATE = "renovate", "Ремонт"
    MASTER_BEDROOM = "master_bedroom", "Мастер-спальня"
    DESIGN_GIFT = "design_gift", "Дизайн-проект в подарок"
    IS_EURO_LAYOUT = "is_euro_layout", "Европланировка"
    SMART_HOUSE = "smart_house", "Умный дом"
    STORES = "stores_count", "Кладовая"
    PENTHOUSE = "is_penthouse", "Пентхаус"
    ANGULAR = "is_angular",  "Квартира угловая"
    AUCTION = "is_auction", "Участвует в аукционе"
    WARDROBE = "wardrobes_count", "Гардеробная"
    TOUR = "is_planoplan", "3D-Тур"
    CITYHOUSE = 'is_cityhouse', 'Ситихаус'
    BATHROOM_WINDOW = 'is_bathroom_window', 'Окно в ванной'
    KITCHEN = 'is_kitchen', 'Кухня'
    FURNITURE = 'is_furniture', 'Мебель'
