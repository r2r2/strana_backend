import pytest
from importlib import import_module

from src.properties.repos import PropertyRepo


@pytest.fixture(scope="function")
def property_repo() -> PropertyRepo:
    property_repo: PropertyRepo = getattr(import_module("src.properties.repos"), "PropertyRepo")()
    return property_repo
