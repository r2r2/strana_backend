import pytest
import faker
import random

from importlib import import_module

from src.faq.repos import FAQRepo


@pytest.fixture(scope="function")
def faq_repo() -> FAQRepo:
    return getattr(import_module("src.faq.repos"), "FAQRepo")()


@pytest.fixture(scope="function")
async def faq_list():
    fake = faker.Faker()
    count = 10
    [await FAQRepo().create(
        dict(
            slug=fake.name(),
            order=random.randint(1, 10),
            question=fake.text()[:10],
            answer=fake.text()[:20]
        )
    )
        for _ in range(count)
    ]
