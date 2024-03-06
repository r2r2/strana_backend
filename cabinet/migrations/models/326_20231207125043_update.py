from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "meetings_meeting" ADD "status_ref_id" VARCHAR(20);
        CREATE TABLE IF NOT EXISTS "meetings_status_meeting_ref" (
    "slug" VARCHAR(20) NOT NULL  PRIMARY KEY,
    "sort" INT NOT NULL  DEFAULT 0,
    "label" VARCHAR(40) NOT NULL,
    "is_final" BOOL NOT NULL  DEFAULT False
);
COMMENT ON COLUMN "meetings_meeting"."status_ref_id" IS 'Статус встречи';
COMMENT ON COLUMN "meetings_status_meeting_ref"."slug" IS 'Слаг';
COMMENT ON COLUMN "meetings_status_meeting_ref"."sort" IS 'Сортировка';
COMMENT ON COLUMN "meetings_status_meeting_ref"."label" IS 'Название статуса встречи';
COMMENT ON COLUMN "meetings_status_meeting_ref"."is_final" IS 'Завершающий статус';
COMMENT ON TABLE "meetings_status_meeting_ref" IS 'Модель статуса встречи.';
        ALTER TABLE "meetings_meeting" ADD CONSTRAINT "fk_meetings_meetings_704c4b5d" FOREIGN KEY ("status_ref_id") REFERENCES "meetings_status_meeting_ref" ("slug") ON DELETE SET NULL;
INSERT INTO meetings_status_meeting_ref ("slug", "sort", "label", "is_final")
SELECT "slug", "sort", "label", "is_final"
FROM meetings_status_meeting;  

UPDATE meetings_meeting b
SET status_ref_id = a.slug
FROM meetings_status_meeting a
WHERE a.id = b.status_id;"""

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "meetings_meeting" DROP CONSTRAINT "fk_meetings_meetings_704c4b5d";
        ALTER TABLE "meetings_meeting" DROP COLUMN "status_ref_id";
        DROP TABLE IF EXISTS "meetings_status_meeting_ref";"""
