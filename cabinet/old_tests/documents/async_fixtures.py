from pytest import fixture


@fixture(scope="function")
async def document(document_repo):
    document = await document_repo.update_or_create({"slug": "test_document"}, {"text": "test {}"})
    return document
