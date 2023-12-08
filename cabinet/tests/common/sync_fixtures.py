from importlib import import_module

from pytest import fixture

from common.amocrm.repos import AmoStatusesRepo


@fixture(scope="function")
def amocrm_class():
    amocrm_class = getattr(import_module("common.amocrm"), "AmoCRM")
    return amocrm_class


@fixture(scope="function")
def bazis_class():
    bazis_class = getattr(import_module("common.bazis.bazis"), "Bazis")
    return bazis_class


@fixture(scope="function")
def global_id_encoder():
    global_id_encoder = getattr(import_module("common.utils"), "to_global_id")
    return global_id_encoder


@fixture(scope="function")
def global_id_decoder():
    global_id_decoder = getattr(import_module("common.utils"), "from_global_id")
    return global_id_decoder


@fixture(scope="function")
def profitbase_class():
    profitbase_class = getattr(import_module("common.profitbase"), "ProfitBase")
    return profitbase_class


@fixture(scope="function")
def common_request_class():
    common_request_class = getattr(import_module("common.requests"), "CommonRequest")
    return common_request_class


@fixture(scope="function")
def common_response_class():
    common_response_class = getattr(import_module("common.requests"), "CommonResponse")
    return common_response_class


@fixture(scope="function")
def graphql_request_class():
    graphql_request_class = getattr(import_module("common.requests"), "GraphQLRequest")
    return graphql_request_class


@fixture(scope="function")
def create_email_token():
    create_email_token = getattr(import_module("common.security"), "create_email_token")
    return create_email_token


@fixture(scope="function")
def hasher():
    hasher = getattr(import_module("common.security"), "get_hasher")()
    return hasher


@fixture(scope="function")
def statuses_repo() -> AmoStatusesRepo:
    status_repo: AmoStatusesRepo = getattr(
        import_module("common.amocrm.repos"), "AmoStatusesRepo"
    )()
    return status_repo
