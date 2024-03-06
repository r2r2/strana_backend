from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_unique_statuses" DROP COLUMN IF EXISTS "can_dispute";
        ALTER TABLE "users_checks_terms"
        ADD COLUMN IF NOT EXISTS "button_id" INT REFERENCES "users_unique_statuses_buttons" ("id") ON DELETE SET NULL;

        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_unique_statuses" ADD COLUMN IF NOT EXISTS "can_dispute" BOOLEAN NOT NULL DEFAULT false;
        ALTER TABLE "users_checks_terms" DROP COLUMN IF EXISTS "button_id";
        """
