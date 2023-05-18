from common import mixins


class UploadPath(mixins.Choices):
    """
    Пути загрузок
    """
    FILES: str = "a/f/f", "Путь загрузки файлов"


class AgencyType(mixins.Choices):
    """
    Тип агенства
    """

    IP: str = "IP", "ИП"
    OOO: str = "OOO", "ООО"


class FileType(mixins.Choices):
    """
    Тип файла
    """
    INN: str = "inn_files",  "ИНН"
    OGRN: str = "ogrn_files", "ОГРН"
    OGRNIP: str = "ogrnip_files", "ОГРНИП"
    CHARTER: str = "charter_files", "Устав"
    PASSPORT: str = "passport_files", "Паспорт"
    COMPANY: str = "company_files", "Карточка предприятия"
    PROCURATORY: str = "procuratory_files", "Доверенность"
