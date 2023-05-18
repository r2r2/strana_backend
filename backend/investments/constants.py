from django.db.models import TextChoices


class ControlComplexityLevel(TextChoices):
    EASY = 'Легко', 'easy'
    MEDIUM = 'Средняя', 'medium'
    HARD = 'Сложно', 'hard'


class LiquidDifficultyLevel(TextChoices):
    EASY = 'Простая', 'easy'
    MEDIUM = 'Средняя', 'medium'
    HARD = 'Высокая', 'hard'
