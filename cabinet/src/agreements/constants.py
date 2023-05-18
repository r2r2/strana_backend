from common import mixins


class AgreementFileType(mixins.Choices):
    """
    Тип файла
    """
    AGREEMENT: str = "agreement_file", "Договор"


class ActFileType(mixins.Choices):
    """
    Тип файла
    """
    ACT: str = "act_file", "Акт"


class AdditionalAgreementFileType(mixins.Choices):
    """
    Тип файла
    """
    ADDITIONALAGREEMENT: str = "additional_agreement_file", "Дополнительное соглашение"
