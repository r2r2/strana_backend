from pytest import mark


@mark.asyncio
class TestCommonRequest(object):
    async def test_request_get(self, mocker, common_request_class, common_response_class):
        mocker.patch("common.requests.CommonRequest.close")
        call_mock = mocker.patch("common.requests.CommonRequest.__call__")
        call_mock.return_value = common_response_class(
            ok=True, data={}, status=200, errors=False, raw=object
        )

        request_get = common_request_class(url="https://example.com", method="GET")

        async with request_get as response_get:
            assert response_get.data is not None
            assert response_get.status is not None
            assert response_get.errors is not None
            assert response_get.raw is not None

    async def test_request_post(self, mocker, common_request_class, common_response_class):
        mocker.patch("common.requests.CommonRequest.close")
        call_mock = mocker.patch("common.requests.CommonRequest.__call__")
        call_mock.return_value = common_response_class(
            ok=True, data={}, status=200, errors=False, raw=object
        )

        request_post = common_request_class(url="https://example.com", method="POST")

        async with request_post as response_post:
            assert response_post.data is not None
            assert response_post.status is not None
            assert response_post.errors is not None
            assert response_post.raw is not None

    async def test_request_delete(self, mocker, common_request_class, common_response_class):
        mocker.patch("common.requests.CommonRequest.close")
        call_mock = mocker.patch("common.requests.CommonRequest.__call__")
        call_mock.return_value = common_response_class(
            ok=True, data={}, status=200, errors=False, raw=object
        )

        request_delete = common_request_class(url="https://example.com", method="POST")

        async with request_delete as response_delete:
            assert response_delete.data is not None
            assert response_delete.status is not None
            assert response_delete.errors is not None
            assert response_delete.raw is not None

    async def test_request_patch(self, mocker, common_request_class, common_response_class):
        mocker.patch("common.requests.CommonRequest.close")
        call_mock = mocker.patch("common.requests.CommonRequest.__call__")
        call_mock.return_value = common_response_class(
            ok=True, data={}, status=200, errors=False, raw=object
        )

        request_patch = common_request_class(url="https://example.com", method="PATCH")

        async with request_patch as response_patch:
            assert response_patch.data is not None
            assert response_patch.status is not None
            assert response_patch.errors is not None
            assert response_patch.raw is not None


@mark.asyncio
class TestGraphQLRequest(object):
    async def test_query(
        self, mocker, backend_config, graphql_request_class, common_response_class
    ):
        mocker.patch("common.requests.GraphQLRequest.close")
        call_mock = mocker.patch("common.requests.GraphQLRequest.__call__")
        call_mock.return_value = common_response_class(
            ok=True, data={}, status=200, errors=False, raw=object
        )

        request = graphql_request_class(
            url=backend_config["url"] + backend_config["graphql"],
            type="globalFlat",
            query_name="globalFlat.graphql",
            query_directory="/src/properties/queries/",
            filters="R2xvYmFsRmxhdFR5cGU6NTIyOTc4OQ==",
        )

        async with request as response:
            assert response is not None
            assert response.data is not None
            assert response.errors is not None
            assert response.status is not None

    async def test_mutation(
        self, mocker, backend_config, graphql_request_class, common_response_class
    ):
        mocker.patch("common.requests.GraphQLRequest.close")
        call_mock = mocker.patch("common.requests.GraphQLRequest.__call__")
        call_mock.return_value = common_response_class(
            ok=True, data={}, status=200, errors=False, raw=object
        )

        request = graphql_request_class(
            url=backend_config["url"] + backend_config["graphql"],
            type="changePropertyStatus",
            query_name="changePropertyStatus.graphql",
            query_directory="/src/booking/queries/",
            filters=("R2xvYmFsRmxhdFR5cGU6NTIyOTc4OQ==", 0),
        )

        async with request as response:
            assert response is not None
            assert response.data is not None
            assert response.errors is not None
            assert response.status is not None
