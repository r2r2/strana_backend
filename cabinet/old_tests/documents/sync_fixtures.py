from importlib import import_module

from pytest import fixture


@fixture(scope="function")
def document_repo():
    document_repo = getattr(import_module("src.documents.repos"), "DocumentRepo")()
    return document_repo
