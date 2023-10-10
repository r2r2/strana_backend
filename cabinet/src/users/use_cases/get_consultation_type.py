from src.users.entities import BaseUserCase
from src.users.repos import ConsultationTypeRepo


class GetConsultationType(BaseUserCase):

    def __init__(
            self,
            consultation_type_repo: type[ConsultationTypeRepo],
    ):
        self.consultation_type_repo = consultation_type_repo()

    async def __call__(self):
        return await self.consultation_type_repo.list()
