from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "payments_purchase_amo_matrix" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "amo_payment_type" INT NOT NULL,
            "default" BOOL NOT NULL  DEFAULT False,
            "priority" INT NOT NULL  DEFAULT 0,
            "mortgage_type_id" INT REFERENCES "payments_mortgage_types" ("id") ON DELETE CASCADE,
            "payment_method_id" INT NOT NULL REFERENCES "payments_payment_method" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "payments_purchase_amo_matrix"."id" IS 'ID';
        COMMENT ON COLUMN "payments_purchase_amo_matrix"."amo_payment_type" IS 'ID Значения в АМО для типа оплаты';
        COMMENT ON COLUMN "payments_purchase_amo_matrix"."default" IS 'По умолчанию';
        COMMENT ON COLUMN "payments_purchase_amo_matrix"."priority" IS 'Приоритет';
        COMMENT ON COLUMN "payments_purchase_amo_matrix"."mortgage_type_id" IS 'Тип ипотеки';
        COMMENT ON COLUMN "payments_purchase_amo_matrix"."payment_method_id" IS 'Способ оплаты';
        COMMENT ON TABLE "payments_purchase_amo_matrix" IS 'Матрица способов оплаты при взаимодействии с АМО.';
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "payments_purchase_amo_matrix";
        """
