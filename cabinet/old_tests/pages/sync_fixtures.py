from pytest import fixture
from importlib import import_module


@fixture(scope="function")
def broker_registration_repo():
    broker_registration_repo = getattr(import_module("src.pages.repos"), "BrokerRegistrationRepo")()
    return broker_registration_repo
