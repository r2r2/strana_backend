from pytest import mark


@mark.asyncio
class TestProfitBase(object):
    async def test_initialization(self, profitbase_class, mocker):
        mocker.patch("common.profitbase.ProfitBase._refresh_auth")
        async with await profitbase_class() as profitbase:
            assert profitbase
