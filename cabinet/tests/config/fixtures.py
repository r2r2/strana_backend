from pytest import fixture
from importlib import import_module


@fixture(scope="function")
def amocrm_config():
    amocrm_config = getattr(import_module("config"), "amocrm_config")
    return amocrm_config
