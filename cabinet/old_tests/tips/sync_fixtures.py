from importlib import import_module

from pytest import fixture


@fixture(scope="function")
def tip_repo():
    tip_repo = getattr(import_module("src.tips.repos"), "TipRepo")()
    return tip_repo
