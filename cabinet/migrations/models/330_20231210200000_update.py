from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "meetings_meeting" ADD "creation_source_ref_id" VARCHAR(20);
        CREATE TABLE IF NOT EXISTS "meetings_meeting_creation_source_ref" (
    "slug" VARCHAR(20) NOT NULL  PRIMARY KEY,
    "label" VARCHAR(40) NOT NULL
);
COMMENT ON COLUMN "meetings_meeting"."creation_source_ref_id" IS 'Источник создания встречи';
COMMENT ON COLUMN "meetings_meeting_creation_source_ref"."slug" IS 'Слаг';
COMMENT ON COLUMN "meetings_meeting_creation_source_ref"."label" IS 'Название источника создания встречи';
COMMENT ON TABLE "meetings_meeting_creation_source_ref" IS 'Модель источника создания встречи.';
        ALTER TABLE "meetings_meeting" ADD CONSTRAINT "fk_meetings_meetings_c934cfe2" FOREIGN KEY ("creation_source_ref_id") REFERENCES "meetings_meeting_creation_source_ref" ("slug") ON DELETE SET NULL;

INSERT INTO meetings_meeting_creation_source_ref ("slug", "label")
SELECT "slug", "label"
FROM meetings_meeting_creation_source;  

UPDATE meetings_meeting b
SET creation_source_ref_id = a.slug
FROM meetings_meeting_creation_source a
WHERE a.id = b.creation_source_id;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "meetings_meeting" DROP CONSTRAINT "fk_meetings_meetings_c934cfe2";
        ALTER TABLE "meetings_meeting" DROP COLUMN "creation_source_ref_id";
        DROP TABLE IF EXISTS "meetings_meeting_creation_source_ref";"""
