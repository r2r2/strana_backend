import pytest
from faker import Faker


@pytest.fixture(scope="class")
def faker() -> Faker:
    """
    Инициализация RU
    """
    faker: Faker = Faker("ru_RU")
    return faker
