import asyncio
from dataclasses import dataclass
from datetime import datetime

from src.notifications.repos import SberbankInvoiceLogRepo


@dataclass
class SberbankInvoiceLogDTO:
    amocrm_id: int
    sent_date: datetime
    sent_email: str
    sent_status: bool | None = None
    sent_error: str | None = None


async def sberbank_invoice_log(log_data: SberbankInvoiceLogDTO) -> asyncio.Task:
    return asyncio.create_task(SberbankInvoiceLogRepo().create(data=log_data.__dict__))
