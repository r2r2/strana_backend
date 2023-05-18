from pytest import fixture
from importlib import import_module


@fixture(scope="function")
def showtime_repo():
    showtime_repo = getattr(import_module("src.showtimes.repos"), "ShowTimeRepo")()
    return showtime_repo
