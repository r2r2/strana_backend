from importlib import import_module

import pytest

from src.mortgage.repos import MortgageTextBlockRepo, MortgageTextBlock


@pytest.fixture(scope="function")
def mortgage_text_block_repo() -> MortgageTextBlockRepo:
    mortgage_text_block_repo: MortgageTextBlockRepo = getattr(
        import_module("src.mortgage.repos"), "MortgageTextBlockRepo"
    )()
    return mortgage_text_block_repo


@pytest.fixture(scope="function")
async def mortgage_text_block(mortgage_text_block_repo, city) -> MortgageTextBlock:
    mortgage_text_block: MortgageTextBlock = await mortgage_text_block_repo.create(
        data=dict(
            title="Test title",
            text="Test text",
            description="Test description",
            slug="test_slug",
            lk_type="lk_type",
        )
    )
    await mortgage_text_block.cities.add(city)
    return mortgage_text_block
