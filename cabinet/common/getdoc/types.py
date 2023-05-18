from enum import Enum
from typing import Optional

from pydantic import BaseModel


class EntityTypes(str, Enum):
    leads = 'leads'


class DoctypeTypes(str, Enum):
    ooo = "OOO"
    ip = "IP"


class ExtensionTypes(str, Enum):
    pdf = "pdf"
    docx = "docx"


class FilenameLeadsTypes(str, Enum):
    stroitrans_ip = "АГЕНТСКИЙ ДОГОВОР Стройтранс №1 ИП .docx"
    stroitrans_ooo = "АГЕНТСКИЙ ДОГОВОР Стройтранс №1 ООО .docx"

    domashnii_ip = "Домашний ИП.docx"
    domashnii_ooo = "Домашний ООО.docx"

    zelenii_mis_ip = "Зеленый мыс ИП.docx"
    zelenii_mis_ooo = "Зеленый мыс ООО.docx"

    kb_eb_ip = "КБ и ЕБ ИП.docx"
    kb_eb_ooo = "КБ и ЕБ ООО.docx"

    strana_zvezdnii_ip = "Страна Звездный ИП.docx"
    strana_zvezdnii_ooo = "Страна Звездный ООО.docx"

    ds_salvador_ip = "ДС 4% Сальвадор К2 ИП.docx"
    ds_salvador_ooo = "ДС 4% Сальвадор К2 ООО.docx"

    ds_domashnii_ip = "ДС 3-3,5% Домашний ИП.docx"
    ds_domashnii_ooo = "ДС 3-3,5% Домашний ООО.docx"

    ds_zvezdnii_ip = "ДС 3-3,5% Звездный ИП.docx"
    ds_zvezdnii_ooo = "ДС 3-3,5% Звездный ООО.docx"

    ds_k2_ip = "ДС 3-3,5% К2 ИП.docx"
    ds_k2_ooo = "ДС 3-3,5% К2 ООО.docx"

    ds_stroiplast_ip = "ДС 3-3,5% Стройтранс доп. ИП.docx"
    ds_stroiplast_ooo = "ДС 3-3,5% Стройтранс ООО.docx"

    spb_78_ip = "Шаблон агентский СПБ ИП 78.docx"
    spb_78_ooo = "Шаблон агентский СПБ ООО 78.docx"

    spb_ip = "Шаблон агентский СПБ ИП.docx"
    spb_ooo = "Шаблон агентский СПБ ООО.docx"

    msk_ip = "Шаблон агентский МСК ИП.docx"
    msk_ooo = "Шаблон агентский МСК ООО.docx"


class GetdocData(BaseModel):
    created_at: int
    filename: str
    format: ExtensionTypes
    name: str
    url: str


class GetdocResponse(BaseModel):
    success: bool
    data: Optional[GetdocData] = None
    error: Optional[str] = None
    error_code: Optional[int] = None


project_filename_mapping = {
    1173629: {DoctypeTypes.ip: FilenameLeadsTypes.kb_eb_ip,
              DoctypeTypes.ooo: FilenameLeadsTypes.kb_eb_ooo},

    1315425: {DoctypeTypes.ip: FilenameLeadsTypes.kb_eb_ip,
              DoctypeTypes.ooo: FilenameLeadsTypes.kb_eb_ooo},

    1173631: {DoctypeTypes.ip: FilenameLeadsTypes.strana_zvezdnii_ip,
              DoctypeTypes.ooo: FilenameLeadsTypes.strana_zvezdnii_ooo},

    1318551: {DoctypeTypes.ip: FilenameLeadsTypes.stroitrans_ip,
              DoctypeTypes.ooo: FilenameLeadsTypes.stroitrans_ooo},

    1331730: {DoctypeTypes.ip: FilenameLeadsTypes.domashnii_ip,
              DoctypeTypes.ooo: FilenameLeadsTypes.domashnii_ooo},

    1331866: {DoctypeTypes.ip: FilenameLeadsTypes.msk_ip,
              DoctypeTypes.ooo: FilenameLeadsTypes.msk_ooo},

    1317091: {DoctypeTypes.ip: FilenameLeadsTypes.spb_78_ip,
              DoctypeTypes.ooo: FilenameLeadsTypes.spb_78_ooo},

    1331022: {DoctypeTypes.ip: FilenameLeadsTypes.spb_ip,
              DoctypeTypes.ooo: FilenameLeadsTypes.spb_ooo},
}
