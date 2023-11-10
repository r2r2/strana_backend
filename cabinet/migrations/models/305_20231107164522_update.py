from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "properties_feature" ADD "profit_id" VARCHAR(64);
        ALTER TABLE "properties_property" ADD "view_square" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "profitbase_property_status" VARCHAR(64);
        ALTER TABLE "properties_property" ADD "window_view_profitbase" VARCHAR(100);
        ALTER TABLE "properties_property" ADD "frontage" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "balconies_count" INT;
        ALTER TABLE "properties_property" ADD "open_plan" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "master_bedroom" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "view_park" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "has_parking" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "corner_windows" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "is_penthouse" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "is_angular" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "view_river" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "has_panoramic_windows" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "has_high_ceiling" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "has_terrace" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "is_discount_enable" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "wardrobes_count" INT;
        ALTER TABLE "properties_property" ADD "loggias_count" INT;
        ALTER TABLE "properties_property" ADD "is_bathroom_window" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "is_cityhouse" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "furnish_price_per_meter" DECIMAL(14,2);
        ALTER TABLE "properties_property" ADD "is_euro_layout" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "ceil_height" VARCHAR(16);
        ALTER TABLE "properties_property" ADD "is_studio" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "has_two_sides_windows" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "smart_house" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "properties_property" ADD "profitbase_booked_until_date" VARCHAR(64);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "properties_feature" DROP COLUMN "profit_id";
        ALTER TABLE "properties_property" DROP COLUMN "view_square";
        ALTER TABLE "properties_property" DROP COLUMN "profitbase_property_status";
        ALTER TABLE "properties_property" DROP COLUMN "window_view_profitbase";
        ALTER TABLE "properties_property" DROP COLUMN "frontage";
        ALTER TABLE "properties_property" DROP COLUMN "balconies_count";
        ALTER TABLE "properties_property" DROP COLUMN "open_plan";
        ALTER TABLE "properties_property" DROP COLUMN "master_bedroom";
        ALTER TABLE "properties_property" DROP COLUMN "view_park";
        ALTER TABLE "properties_property" DROP COLUMN "has_parking";
        ALTER TABLE "properties_property" DROP COLUMN "corner_windows";
        ALTER TABLE "properties_property" DROP COLUMN "is_penthouse";
        ALTER TABLE "properties_property" DROP COLUMN "is_angular";
        ALTER TABLE "properties_property" DROP COLUMN "view_river";
        ALTER TABLE "properties_property" DROP COLUMN "has_panoramic_windows";
        ALTER TABLE "properties_property" DROP COLUMN "has_high_ceiling";
        ALTER TABLE "properties_property" DROP COLUMN "has_terrace";
        ALTER TABLE "properties_property" DROP COLUMN "is_discount_enable";
        ALTER TABLE "properties_property" DROP COLUMN "wardrobes_count";
        ALTER TABLE "properties_property" DROP COLUMN "loggias_count";
        ALTER TABLE "properties_property" DROP COLUMN "is_bathroom_window";
        ALTER TABLE "properties_property" DROP COLUMN "is_cityhouse";
        ALTER TABLE "properties_property" DROP COLUMN "furnish_price_per_meter";
        ALTER TABLE "properties_property" DROP COLUMN "is_euro_layout";
        ALTER TABLE "properties_property" DROP COLUMN "ceil_height";
        ALTER TABLE "properties_property" DROP COLUMN "is_studio";
        ALTER TABLE "properties_property" DROP COLUMN "has_two_sides_windows";
        ALTER TABLE "properties_property" DROP COLUMN "smart_house";
        ALTER TABLE "properties_property" DROP COLUMN "profitbase_booked_until_date";"""
