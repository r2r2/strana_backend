-- upgrade --
ALTER TABLE "booking_booking" ADD "payment_method" VARCHAR(20);
ALTER TABLE "booking_booking" ADD "maternal_capital" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" ADD "housing_certificate" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "booking_booking" ADD "government_loan" BOOL NOT NULL  DEFAULT False;
COMMENT ON COLUMN "booking_booking"."payment_method" IS 'Способ покупки';
COMMENT ON COLUMN "booking_booking"."maternal_capital" IS 'Материнский капитал (способ покупки)';
COMMENT ON COLUMN "booking_booking"."housing_certificate" IS 'Жилищный сертификат (способ покупки)';
COMMENT ON COLUMN "booking_booking"."government_loan" IS 'Государственный займ (способ покупки)';
-- downgrade --
ALTER TABLE "booking_booking" DROP COLUMN "payment_method";
ALTER TABLE "booking_booking" DROP COLUMN "maternal_capital";
ALTER TABLE "booking_booking" DROP COLUMN "housing_certificate";
ALTER TABLE "booking_booking" DROP COLUMN "government_loan";
