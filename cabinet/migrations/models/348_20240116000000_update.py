from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        alter table "questionnaire_upload_documents" add column if not exists "mortgage_ticket_id" int null;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        alter table "questionnaire_upload_documents" drop column if exists "mortgage_ticket_id";
        """
