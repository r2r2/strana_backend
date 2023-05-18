from pytest import mark

from src.booking.constants import PaymentMethods


@mark.asyncio
class TestOnlinePurchaseStartedHistoryMessage(object):
    async def test(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/purchase_start.txt", {}
        )
        assert rendered_message == "<p>Согласился с офертой об условиях онлайн-покупки.</p>"


@mark.asyncio
class TestPaymentMethodHistoryMessage(object):
    async def test_cash_payment_method(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/payment_method_select.txt",
            {
                "payment_method": "cash",
                "maternal_capital": True,
                "housing_certificate": True,
                "government_loan": True,
                "bank_name": None,
                "instruments_count": 3,
            },
        )
        assert rendered_message == (
            "<p>Выбрал способ покупки «Собственные средства» с дополнительными инструментами в "
            "виде материнского капитала, жилищного сертификата и государственного займа.</p>"
        )

    async def test_mortgage_payment_method(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/payment_method_select.txt",
            {
                "payment_method": "mortgage",
                "maternal_capital": True,
                "housing_certificate": True,
                "government_loan": True,
                "bank_name": "test_bank_name",
                "instruments_count": 3,
            },
        )
        assert rendered_message == (
            "<p>Выбрал способ покупки «Ипотека» с дополнительными инструментами в виде "
            "материнского капитала, жилищного сертификата и государственного "
            "займа.</p><p>Отправил данные для связи с ипотечным банковским "
            "специалистом.</p><ul><li><i>Название банка:</i> test_bank_name</li></ul>"
        )

    async def test_installment_plan_payment_method(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/payment_method_select.txt",
            {
                "payment_method": "installment_plan",
                "maternal_capital": True,
                "housing_certificate": True,
                "government_loan": True,
                "bank_name": None,
                "instruments_count": 3,
            },
        )
        assert rendered_message == (
            "<p>Выбрал способ покупки «Рассрочка» с дополнительными инструментами в виде "
            "материнского капитала, жилищного сертификата и государственного займа.</p>"
        )

    async def test_two_instruments(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/payment_method_select.txt",
            {
                "payment_method": "cash",
                "maternal_capital": True,
                "housing_certificate": True,
                "government_loan": False,
                "bank_name": None,
                "instruments_count": 2,
            },
        )
        assert rendered_message == (
            "<p>Выбрал способ покупки «Собственные средства» с дополнительными инструментами в "
            "виде материнского капитала и жилищного сертификата.</p>"
        )

        rendered_message = await history_service.render_message(
            "src/booking/templates/history/payment_method_select.txt",
            {
                "payment_method": "cash",
                "maternal_capital": True,
                "housing_certificate": False,
                "government_loan": True,
                "bank_name": None,
                "instruments_count": 2,
            },
        )
        assert rendered_message == (
            "<p>Выбрал способ покупки «Собственные средства» с дополнительными инструментами в "
            "виде материнского капитала и государственного займа.</p>"
        )

        rendered_message = await history_service.render_message(
            "src/booking/templates/history/payment_method_select.txt",
            {
                "payment_method": "cash",
                "maternal_capital": False,
                "housing_certificate": True,
                "government_loan": True,
                "bank_name": None,
                "instruments_count": 2,
            },
        )
        assert rendered_message == (
            "<p>Выбрал способ покупки «Собственные средства» с дополнительными инструментами в "
            "виде жилищного сертификата и государственного займа.</p>"
        )

    async def test_one_instrument(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/payment_method_select.txt",
            {
                "payment_method": "cash",
                "maternal_capital": True,
                "housing_certificate": False,
                "government_loan": False,
                "bank_name": None,
                "instruments_count": 1,
            },
        )
        assert rendered_message == (
            "<p>Выбрал способ покупки «Собственные средства» с дополнительным инструментом в виде "
            "материнского капитала.</p>"
        )

        rendered_message = await history_service.render_message(
            "src/booking/templates/history/payment_method_select.txt",
            {
                "payment_method": "cash",
                "maternal_capital": False,
                "housing_certificate": True,
                "government_loan": False,
                "bank_name": None,
                "instruments_count": 1,
            },
        )
        assert rendered_message == (
            "<p>Выбрал способ покупки «Собственные средства» с дополнительным инструментом в виде "
            "жилищного сертификата.</p>"
        )

        rendered_message = await history_service.render_message(
            "src/booking/templates/history/payment_method_select.txt",
            {
                "payment_method": "cash",
                "maternal_capital": False,
                "housing_certificate": False,
                "government_loan": True,
                "bank_name": None,
                "instruments_count": 1,
            },
        )
        assert rendered_message == (
            "<p>Выбрал способ покупки «Собственные средства» с дополнительным инструментом в виде "
            "государственного займа.</p>"
        )

    async def test_no_instruments(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/payment_method_select.txt",
            {
                "payment_method": "cash",
                "maternal_capital": False,
                "housing_certificate": False,
                "government_loan": False,
                "bank_name": None,
                "instruments_count": 0,
            },
        )
        assert rendered_message == "<p>Выбрал способ покупки «Собственные средства».</p>"

    async def test_constant_instrument_is_supported(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/payment_method_select.txt",
            {
                "payment_method": PaymentMethods.CASH,
                "maternal_capital": True,
                "housing_certificate": True,
                "government_loan": True,
                "bank_name": None,
                "instruments_count": 3,
            },
        )
        assert rendered_message == (
            "<p>Выбрал способ покупки «Собственные средства» с дополнительными инструментами в виде "
            "материнского капитала, жилищного сертификата и государственного займа.</p>"
        )


@mark.asyncio
class TestAmocrmAgentDataValidatedHistoryMessage(object):
    async def test(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/amocrm_webhook_access_deal.txt", {}
        )
        assert rendered_message == "<p>Данные по ипотеке были подтверждены.</p>"


@mark.asyncio
class TestDDUCreatedHistoryMessage(object):
    async def test(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/ddu_create.txt", {}
        )
        assert rendered_message == "<p>Отправил данные для оформления ДДУ.</p>"


@mark.asyncio
class TestDDUUpdatedHistoryMessage(object):
    async def test(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/ddu_update.txt", {}
        )
        assert rendered_message == "<p>Изменил данные для оформления ДДУ.</p>"


@mark.asyncio
class TestAmocrmDDUUploadedByLawyerHistoryMessage(object):
    async def test(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/ddu_upload.txt", {}
        )
        assert rendered_message == "<p>ДДУ сформирован и направлен на согласование.</p>"


@mark.asyncio
class TestDDUAcceptedHistoryMessage(object):
    async def test(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/ddu_accept.txt", {}
        )
        assert rendered_message == "<p>Согласился с условиями ДДУ.</p>"


@mark.asyncio
class TestEscrowUploadedHistoryMessage(object):
    async def test(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/escrow_upload.txt", {}
        )
        assert rendered_message == "<p>Отправил документ об открытии эскроу-счёта.</p>"


@mark.asyncio
class TestAmocrmSigningDateSetHistoryMessage(object):
    async def test(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/amocrm_webhook_date_deal.txt", {}
        )
        assert rendered_message == "<p>Дата подписания ДДУ была назначена.</p>"


@mark.asyncio
class TestAmocrmSignedHistoryMessage(object):
    async def test(self, client, history_service) -> None:
        rendered_message = await history_service.render_message(
            "src/booking/templates/history/amocrm_webhook_deal_success.txt", {}
        )
        assert rendered_message == "<p>Перешёл на этап ДДУ зарегистрирован.</p>"
