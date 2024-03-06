from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "privilege_category_m2m_city";
        DROP TABLE IF EXISTS "privilege_program";
        DROP TABLE IF EXISTS "privilege_request";
        DROP TABLE IF EXISTS "privilege_category";
        DROP TABLE IF EXISTS "privilege_subcategory";
        DROP TABLE IF EXISTS "privilege_company";
        DROP TABLE IF EXISTS "privilege_cooperation_type";"""
