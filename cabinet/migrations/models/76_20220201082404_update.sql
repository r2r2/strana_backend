-- upgrade --
ALTER TABLE "booking_purchase_help_text" ADD "default" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "booking_purchase_help_text" DROP COLUMN "default";
