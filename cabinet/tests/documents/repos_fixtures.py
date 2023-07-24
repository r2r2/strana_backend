import pytest
from importlib import import_module

from src.documents.repos import InstructionRepo


@pytest.fixture(scope="function")
def instruction_repo() -> InstructionRepo:
    instruction_repo: InstructionRepo = getattr(import_module("src.documents.repos"), "InstructionRepo")()
    return instruction_repo


@pytest.fixture(scope="function")
async def instruction_fixture(instruction_repo, city) -> None:
    instruction_data: dict = dict(
        slug="slug",
        link_text="text",
    )
    await instruction_repo.create(data=instruction_data)
