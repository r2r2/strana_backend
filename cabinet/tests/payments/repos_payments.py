import pytest
from importlib import import_module


from src.payments.repos import (
    PurchaseAmoMatrixRepo,
    PurchaseAmoMatrix,
    PaymentMethodRepo,
    PaymentMethod,
    MortgageTypeRepo,
    MortgageType,
    PropertyPriceTypeRepo,
    PropertyPriceType,
    PriceOfferMatrixRepo,
    PriceOfferMatrix,
    PropertyPriceRepo,
    PropertyPrice,
)


@pytest.fixture(scope="function")
def mortgage_type_repo() -> MortgageTypeRepo:
    return getattr(import_module("src.payments.repos"), "MortgageTypeRepo")()


@pytest.fixture(scope="function")
async def mortgage_type(mortgage_type_repo, faker) -> MortgageType:
    data = {
        "title": faker.name(),
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
        "by_dev": False,
    }
    mortgage_type = await mortgage_type_repo.create(data)
    return mortgage_type


@pytest.fixture(scope="function")
def payment_method_repo() -> PaymentMethodRepo:
    return getattr(import_module("src.payments.repos"), "PaymentMethodRepo")()


@pytest.fixture(scope="function")
async def payment_method(payment_method_repo, faker) -> PaymentMethod:
    data = {
        "name": faker.word(),
        "amocrm_id": faker.random_int(min=10000000, max=99999999),
    }
    payment_method = await payment_method_repo.update_or_create(
        filters={"slug": "test_slug"},
        data=data,
    )
    return payment_method


@pytest.fixture(scope="function")
def purchase_amo_matrix_repo() -> PurchaseAmoMatrixRepo:
    return getattr(import_module("src.payments.repos"), "PurchaseAmoMatrixRepo")()


@pytest.fixture(scope="function")
async def purchase_amo_matrix(
    purchase_amo_matrix_repo,
    mortgage_type,
    payment_method,
    faker,
) -> PurchaseAmoMatrix:
    data = {
        "payment_method_id": payment_method.id,
        "mortgage_type_id": mortgage_type.id,
        "amo_payment_type": faker.random_int(min=100, max=999),
    }
    purchase_amo_matrix = await purchase_amo_matrix_repo.create(data)
    return purchase_amo_matrix


@pytest.fixture(scope="function")
def property_price_type_repo() -> PropertyPriceTypeRepo:
    return getattr(import_module("src.payments.repos"), "PropertyPriceTypeRepo")()


@pytest.fixture(scope="function")
def property_price_repo() -> PropertyPriceRepo:
    return getattr(import_module("src.payments.repos"), "PropertyPriceRepo")()


@pytest.fixture(scope="function")
async def property_price_type(
    property_price_type_repo,
    faker,
) -> PropertyPriceType:
    data = {
        "name": faker.word(),
        "slug": faker.word(),
    }
    property_price_type = await property_price_type_repo.create(data)
    return property_price_type


@pytest.fixture(scope="function")
async def property_price_type_default(
    property_price_type_repo,
    faker,
) -> PropertyPriceType:
    data = {
        "name": faker.word(),
        "slug": faker.word(),
        "default": True,
    }
    property_price_type = await property_price_type_repo.create(data)
    return property_price_type


@pytest.fixture(scope="function")
async def property_price(
    property_price_repo,
    property_price_type,
    property,
    faker,
) -> PropertyPrice:
    data = {
        "property_id": property.id,
        "price": faker.random_int(min=1000000, max=9999999),
        "price_type_id": property_price_type.id,
    }
    property_price = await property_price_repo.create(data)
    return property_price


@pytest.fixture(scope="function")
async def property_price_default(
    property_price_repo,
    property_price_type_default,
    property,
    faker,
) -> PropertyPrice:
    data = {
        "property_id": property.id,
        "price": faker.random_int(min=1000000, max=9999999),
        "price_type_id": property_price_type_default.id,
    }
    property_price = await property_price_repo.create(data)
    return property_price


@pytest.fixture(scope="function")
def property_offer_matrix_repo() -> PriceOfferMatrixRepo:
    return getattr(import_module("src.payments.repos"), "PriceOfferMatrixRepo")()


@pytest.fixture(scope="function")
async def property_offer_matrix(
    property_offer_matrix_repo,
    payment_method,
    property_price_type,
    mortgage_type,
    faker,
) -> PriceOfferMatrix:
    data = {
        "name": faker.word(),
        "payment_method_id": payment_method.id,
        "price_type_id": property_price_type.id,
        "mortgage_type_id": mortgage_type.id,
    }
    property_offer_matrix = await property_offer_matrix_repo.create(data)
    return property_offer_matrix


@pytest.fixture(scope="function")
async def property_offer_matrix_default(
    property_offer_matrix_repo,
    payment_method,
    property_price_type,
    mortgage_type,
    faker,
) -> PriceOfferMatrix:
    data = {
        "name": faker.word(),
        "default": True,
    }
    property_offer_matrix = await property_offer_matrix_repo.create(data)
    return property_offer_matrix
