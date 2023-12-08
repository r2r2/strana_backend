from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "booking_tags_booking_source_through" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "booking_source_id" INT NOT NULL REFERENCES "booking_source" ("id") ON DELETE CASCADE,
            "tag_id" INT NOT NULL REFERENCES "booking_bookingtag" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "booking_tags_booking_source_through"."id" IS 'ID';
        COMMENT ON COLUMN "booking_tags_booking_source_through"."booking_source_id" IS 'Источник бронирования';
        COMMENT ON COLUMN "booking_tags_booking_source_through"."tag_id" IS 'Тег';
        
        CREATE TABLE IF NOT EXISTS "booking_tags_system_through" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "system_id" INT NOT NULL REFERENCES "settings_system_list" ("id") ON DELETE CASCADE,
            "tag_id" INT NOT NULL REFERENCES "booking_bookingtag" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "booking_tags_system_through"."id" IS 'ID';
        COMMENT ON COLUMN "booking_tags_system_through"."system_id" IS 'Система';
        COMMENT ON COLUMN "booking_tags_system_through"."tag_id" IS 'Тег';
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "booking_tags_booking_source_through";
        DROP TABLE IF EXISTS "booking_tags_system_through";
        """
