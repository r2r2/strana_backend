-- upgrade --
ALTER TABLE "properties_property" ADD "preferential_mortgage" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "properties_property" ADD "maternal_capital" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "properties_property" DROP COLUMN "preferential_mortgage";
ALTER TABLE "properties_property" DROP COLUMN "maternal_capital";
