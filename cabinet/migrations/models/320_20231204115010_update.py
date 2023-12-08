from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "mortgage_submitted_proposal" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mortgage_application" INT NOT NULL,
    "name" TEXT NOT NULL,
    "external_code" TEXT NOT NULL
);
COMMENT ON COLUMN "mortgage_submitted_proposal"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_submitted_proposal"."mortgage_application" IS 'Заявка ан ипотеку';
COMMENT ON COLUMN "mortgage_submitted_proposal"."name" IS 'Название предложения';
COMMENT ON COLUMN "mortgage_submitted_proposal"."external_code" IS 'Внешний код';
COMMENT ON TABLE "mortgage_submitted_proposal" IS 'Поданные предложения.';
        CREATE TABLE IF NOT EXISTS "mortgage_canlutator_submitted_proposal_offer_through" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mortgage_offer_id" INT NOT NULL REFERENCES "mortgage_calculator_offer" ("id") ON DELETE CASCADE,
    "mortgage_proposal_id" INT NOT NULL REFERENCES "mortgage_submitted_proposal" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "mortgage_canlutator_submitted_proposal_offer_through"."id" IS 'ID';
COMMENT ON COLUMN "mortgage_canlutator_submitted_proposal_offer_through"."mortgage_offer_id" IS 'Из ип предложений в поданные предложения';
COMMENT ON COLUMN "mortgage_canlutator_submitted_proposal_offer_through"."mortgage_proposal_id" IS 'Из поданных предложений в ип предложения';
COMMENT ON TABLE "mortgage_canlutator_submitted_proposal_offer_through" IS 'Связь подданых приложений с ип';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "mortgage_calculator_proposal_offers_through" cascade;
        DROP TABLE IF EXISTS "mortgage_submitted_proposal cascade";
        DROP TABLE IF EXISTS "mortgage_canlutator_submitted_proposal_offer_through cascade";"""
