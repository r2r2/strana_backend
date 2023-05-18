from pytest import mark

from src.documents.use_cases import GetDocumentCase


@mark.asyncio
class TestGetDocumentView(object):
    async def test_not_found(self, client):
        response = await client.get("/documents")
        response_status = response.status_code

        awaitable_status = 404

        assert response_status == awaitable_status

    async def test_get_price_text(self):
        text = GetDocumentCase._get_price_text(10001)
        assert text == "10001.00 рубль (Десять тысяч один рубль ноль копеек)"

        text = GetDocumentCase._get_price_text(10002)
        assert text == "10002.00 рубля (Десять тысяч два рубля ноль копеек)"

        text = GetDocumentCase._get_price_text(10000)
        assert text == "10000.00 рублей (Десять тысяч рублей ноль копеек)"

        text = GetDocumentCase._get_price_text(50000)
        assert text == "50000.00 рублей (Пятьдесят тысяч рублей ноль копеек)"

    async def test_get_period_text(self):
        text = GetDocumentCase._get_period_text(1)
        assert text == "1 (Один) календарный день"

        text = GetDocumentCase._get_period_text(2)
        assert text == "2 (Два) календарных дня"

        text = GetDocumentCase._get_period_text(10)
        assert text == "10 (Десять) календарных дней"

        text = GetDocumentCase._get_period_text(20)
        assert text == "20 (Двадцать) календарных дней"
