from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_payment_page_notifications" ADD "slug" VARCHAR(100);
        ALTER TABLE "booking_payment_page_notifications" ALTER COLUMN "title" TYPE VARCHAR(100) USING "title"::VARCHAR(100);
        INSERT INTO "booking_payment_page_notifications" ("title", "notify_text", "button_text", "slug")
        VALUES ('Оплата прошла успешно', 'Текст уведомления', 'Текст кнопки', 'success'),
               ('Оплата прошла неудачно (есть продления резервирования)', 'Текст уведомления', 'Текст кнопки', 'failure'),
               ('Оплата прошла неудачно (есть нет продлений резервирования)', 'Текст уведомления', 'Текст кнопки', 'failure_with_continuation');
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "booking_payment_page_notifications" DROP COLUMN "slug";
        ALTER TABLE "booking_payment_page_notifications" ALTER COLUMN "title" TYPE VARCHAR(50) USING "title"::VARCHAR(50);"""
