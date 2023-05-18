from django.db.models import TextChoices, IntegerChoices


class NewsType(TextChoices):
    NEWS = "news", "Новость"
    ACTION = "action", "Акция"
    PROGRESS = "progress", "Ход строительства"
    VIDEO = "video", "Видео"
    STREAM = "stream", "Онлайн трансляция"
    ABOUT_US = "about_us", "СМИ о нас"
    ACTION_LANDING = "action_landing", "Промо-лендинг"

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
