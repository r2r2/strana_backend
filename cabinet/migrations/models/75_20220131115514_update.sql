-- upgrade --
CREATE TABLE IF NOT EXISTS "booking_purchase_help_text" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" TEXT NOT NULL,
    "booking_online_purchase_step" VARCHAR(50) NOT NULL,
    "payment_method" VARCHAR(20) NOT NULL,
    "maternal_capital" BOOL NOT NULL,
    "certificate" BOOL NOT NULL,
    "loan" BOOL NOT NULL
);
-- downgrade --
DROP TABLE IF EXISTS "booking_purchase_help_text";
