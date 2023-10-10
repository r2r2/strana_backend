from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "booking_payment_page_notifications" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "title" VARCHAR(50) NOT NULL,
            "notify_text" TEXT NOT NULL,
            "button_text" VARCHAR(50) NOT NULL
        );
        COMMENT ON COLUMN "booking_payment_page_notifications"."id" IS 'ID';
        COMMENT ON COLUMN "booking_payment_page_notifications"."title" IS 'Заголовок';
        COMMENT ON COLUMN "booking_payment_page_notifications"."notify_text" IS 'Текст уведомления';
        COMMENT ON COLUMN "booking_payment_page_notifications"."button_text" IS 'Текст кнопки';
        COMMENT ON TABLE "booking_payment_page_notifications" IS 'Уведомления страницы успешной оплаты';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "booking_payment_page_notifications";
    """
