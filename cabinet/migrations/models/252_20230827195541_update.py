from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "amocrm_amocrm_settings" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "client_id" TEXT NOT NULL,
            "client_secret" TEXT NOT NULL,
            "access_token" TEXT,
            "refresh_token" TEXT,
            "redirect_uri" VARCHAR(255) NOT NULL
        );
        COMMENT ON COLUMN "amocrm_amocrm_settings"."id" IS 'ID';
        COMMENT ON COLUMN "amocrm_amocrm_settings"."client_id" IS 'Client ID';
        COMMENT ON COLUMN "amocrm_amocrm_settings"."client_secret" IS 'Client Secret';
        COMMENT ON COLUMN "amocrm_amocrm_settings"."access_token" IS 'Access Token';
        COMMENT ON COLUMN "amocrm_amocrm_settings"."refresh_token" IS 'Refresh Token';
        COMMENT ON COLUMN "amocrm_amocrm_settings"."redirect_uri" IS 'Redirect URL';
        COMMENT ON TABLE "amocrm_amocrm_settings" IS 'Настройки AmoCRM';;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "amocrm_amocrm_settings";
    """
