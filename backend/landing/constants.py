from django.db.models import TextChoices


class CTABlockType(TextChoices):
    PRESENTATION = "presentation", "Презентация"
    INSTRUCTION = "instruction", "Инструкция"


class LandingBlockChoices(TextChoices):
    # PascalCase по просбе фронта
    ONE_IMAGE = "OneImage", "Блок с текстом и одним изображением"
    TWO_IMAGE = "TwoImage", "Блок с двумя изображениями и описаниями к ним"
    THREE_IMAGE = "ThreeImage", "Блок с коллажом из трех изображений"
    TITLE_TEXT = "TitleText", "Блок с заголовком и текстом"
    IMAGE = "Image", "Изображение"
    PANORAMA = "Panorama", "Панорама"
    SLIDER = "Slider", "Блок со слайдером"
    SIMPLE_CTA = "SimpleCta", "Простой блок CTA"
    TEXT_LIST = "TextList", "Блок с текстом и списком"
    TWO_COLUMN = "TwoColumn", "Блок с иконками в две колонки"
    FURNISH = "Furnish", "Блок с отделкой"
    DIGITS = "Digits", "Блок с цифрами"
    FLATS = "Flats", "Блок квартир"
    ADVANTAGE = "Advantage", "Блок преимуществ"
    STEPS = "Steps", "Блок шаги"
    MORTGAGE = "Mortgage", "Блок с ипотекой"
    PROGRESS = "Progress", "Ход строительства"
    FORMS = "Forms", "Блок с формами"
    NEWS = "News", "Блок с новостями"
