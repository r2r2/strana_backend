from django.db.models import IntegerChoices, TextChoices


class PurchasePurposeChoices(IntegerChoices):
    INVEST = 0, "Инвестирование"
    SELF = 1, "Для себя"


class FormPayChoices(IntegerChoices):
    MORTGAGE = 714855, "Ипотека"
    ALL = 714853, "100% оплата"
    CASH_MSK = 714859, "Наличные+мск"
    INSTALLMENTS = 714861, "Рассрочка"
    SERT = 714863, "Сертификат"
    MORTGAGE_MSK = 1284003, "ипотека+мск"
    MORTGAGE_SERT = 1315751, "ипотека+сертификат"
    CASH_SERT = 1315753, "наличные+сертификат"
    CASH_SERT_LOAN = 1317511, "наличные+сертификат+займ"
    CASH_MORTGAGE_SERT_LOAN = 1317513, "наличные+ипотека+сертификат+займ"
    CASH_SERT_LOAN_MSK = 1317551, "наличные+сертификат+займ+мск"
    MORTGAGE_SUB_MSK = 1317705, "ипотека субсидированная+МСК"
    MORTGAGE_LOAN_SERT_MSK = 1318019, "ипотека+займ+сертификат+МСК"
    INSTALLMENTS_MSK = 1324226, "рассрочка+мск"


class NextMeetingTypeChoices(IntegerChoices):
    MEETING = 1323738, "Встреча"
    VIDEO = 1323780, "Видеоконференция"
    TAXI = 1325332, "Встреча с такси"
    KOLUMB = 1327588, "Встреча во Флеш Офисе Колумб"
    SITY_MOLL = 1327590, "Встреча во Флеш Офисе Сити молл"


class MeetingEndTypeChoices(IntegerChoices):
    APPOINTED = 1, "Встреча назначена."
    IN_PROGRESS = 2, "Идет встреча."
    DECIDE = 3, "Принимает решение"
    REPEAT = 4, "Повторная встреча"
    BOOKING = 5, "Бронь"
    CANCEL = 6, "Отказ"


class AnotherTypeChoices(IntegerChoices):
    STORAGE = 0, "Кладовое помещение"
    PARKING = 1, "Парковочное место"
    COMMERCIAL = 2, "Коммерция"
    APART = 3, "Апартаменты"


class RoomsChoices(IntegerChoices):
    STUDY = 1064019, "Студия"
    ONE = 1064021, "1-ком"
    TWO = 1064023, "2-ком"
    THREE = 1064027, "3-ком"
    FOUR = 1064029, "4-ком"
    TWO_EURO = 1064025, "2E"
    THREE_EURO = 1217243, "3E"
    FOUR_EURO = 1325414, "4E"
    FIVE = 1217247, "5-ком+"


class RoomsChoicesForSpecs(IntegerChoices):
    STUDY = 1064019, "Студия"
    ONE = 1064021, "1"
    TWO = 1064023, "2"
    THREE = 1064027, "3"
    FOUR = 1064029, "4"
    TWO_EURO = 1064025, "2E"
    THREE_EURO = 1217243, "3E"
    FOUR_EURO = 1325414, "4E"
    FIVE = 1217247, "5+"


class AppointmentResultChoices(IntegerChoices):
    NOT_ACCEPTED = 0, "Помещение не принято, дефекты есть"
    ACCEPTED_DEFECTS = 1, "Помещение принято, дефекты есть"
    ACCEPTED = 2, "Помещение принято, дефектов нет"


class ProgressQuarter(IntegerChoices):
    FIRST = 1, "I"
    SECOND = 2, "II"
    THIRD = 3, "III"
    FOURTH = 4, "IV"


class ProgressMonth(TextChoices):
    JANUARY = "january", "Январь"
    FEBRUARY = "february", "Февраль"
    MARCH = "march", "Март"
    APRIL = "april", "Апрель"
    MAY = "may", "Май"
    JUNE = "june", "Июнь"
    JULY = "july", "Июль"
    AUGUST = "august", "Август"
    SEPTEMBER = "september", "Сентябрь"
    OCTOBER = "october", "Октябрь"
    NOVEMBER = "november", "Ноябрь"
    DECEMBER = "december", "Декабрь"
