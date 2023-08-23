-- upgrade --
ALTER TABLE "main_page_offer" ALTER COLUMN "priority" SET DEFAULT 0;
ALTER TABLE "main_page_offer" ALTER COLUMN "priority" SET NOT NULL;
ALTER TABLE "main_page_partner_logo" ALTER COLUMN "priority" SET DEFAULT 0;
ALTER TABLE "main_page_partner_logo" ALTER COLUMN "priority" SET NOT NULL;
ALTER TABLE "main_page_sell_online" ALTER COLUMN "priority" SET DEFAULT 0;
ALTER TABLE "main_page_sell_online" ALTER COLUMN "priority" SET NOT NULL;
-- downgrade --
ALTER TABLE "main_page_offer" ALTER COLUMN "priority" DROP NOT NULL;
ALTER TABLE "main_page_offer" ALTER COLUMN "priority" DROP DEFAULT;
ALTER TABLE "main_page_sell_online" ALTER COLUMN "priority" DROP NOT NULL;
ALTER TABLE "main_page_sell_online" ALTER COLUMN "priority" DROP DEFAULT;
ALTER TABLE "main_page_partner_logo" ALTER COLUMN "priority" DROP NOT NULL;
ALTER TABLE "main_page_partner_logo" ALTER COLUMN "priority" DROP DEFAULT;