from ..entities import BasePrivilegeServiceCase
from ..exceptions import PrivilegeProgramNotFoundError
from ..repos import PrivilegeProgramRepo, PrivilegeProgram


class ProgramDetailCase(BasePrivilegeServiceCase):
    """
    Кейс получения детальной карточки программы
    """

    def __init__(
        self,
        program_repo: type[PrivilegeProgramRepo],
    ) -> None:
        self.program_repo: PrivilegeProgramRepo = program_repo()

    async def __call__(self, program_slug: str) -> PrivilegeProgram:
        active_filters: dict = dict(is_active=True, slug=program_slug)
        program: PrivilegeProgram = await self.program_repo.retrieve(
            filters=active_filters,
            prefetch_fields=["partner_company", "subcategory"],
        )
        if not program:
            raise PrivilegeProgramNotFoundError
        return program
