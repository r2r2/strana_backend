from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "meetings_meeting" ADD "creation_source_id" INT;
        
        CREATE TABLE IF NOT EXISTS "meetings_meeting_creation_source" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "slug" VARCHAR(20) NOT NULL UNIQUE,
            "label" VARCHAR(40) NOT NULL
        );
        COMMENT ON COLUMN "meetings_meeting"."creation_source_id" IS 'Источник создания встречи';
        COMMENT ON COLUMN "meetings_meeting_creation_source"."id" IS 'ID';
        COMMENT ON COLUMN "meetings_meeting_creation_source"."slug" IS 'Слаг';
        COMMENT ON COLUMN "meetings_meeting_creation_source"."label" IS 'Название источника создания встречи';
        COMMENT ON TABLE "meetings_meeting_creation_source" IS 'Модель источника создания встречи.';

        ALTER TABLE "meetings_meeting" ADD CONSTRAINT "fk_meetings_meetings_6d322d81" FOREIGN KEY ("creation_source_id") REFERENCES "meetings_meeting_creation_source" ("id") ON DELETE SET NULL;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "meetings_meeting" DROP CONSTRAINT "fk_meetings_meetings_6d322d81";
        ALTER TABLE "meetings_meeting" DROP COLUMN "creation_source_id";
        DROP TABLE IF EXISTS "meetings_meeting_creation_source";
        """
