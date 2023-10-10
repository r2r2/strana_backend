from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users_dispute_statuses" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL
);
INSERT INTO "users_dispute_statuses" ("title")
VALUES ('В работе'),
       ('Отказ'),
       ('Успешно');
COMMENT ON COLUMN "users_dispute_statuses"."id" IS 'ID';
COMMENT ON COLUMN "users_dispute_statuses"."title" IS 'Название';
ALTER TABLE "users_checks" ADD "dispute_status_id" INT;
ALTER TABLE "users_checks" ADD CONSTRAINT "fk_users_dispute_status_dad26694" FOREIGN KEY ("dispute_status_id") REFERENCES "users_dispute_statuses" ("id") ON DELETE SET NULL;
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    ALTER TABLE "users_checks" DROP CONSTRAINT "fk_users_dispute_status_dad26694";
    ALTER TABLE "users_checks" DROP COLUMN "dispute_status_id";
    DROP TABLE IF EXISTS "users_dispute_statuses";      
"""
