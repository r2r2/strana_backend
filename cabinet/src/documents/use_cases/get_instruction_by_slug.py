from typing import Any, Type

from ..entities import BaseDocumentCase
from ..exceptions import InstructionNotFoundError
from ..repos import Instruction, InstructionRepo


class GetSlugInstructionCase(BaseDocumentCase):
    """
    Получение инструкции по слагу.
    """

    def __init__(self, instruction_repo: Type[InstructionRepo]) -> None:
        self.instruction_repo: InstructionRepo = instruction_repo()

    async def __call__(self, slug: str) -> Instruction:
        filters: dict[str, Any] = dict(slug=slug)
        instruction: Instruction = await self.instruction_repo.retrieve(filters=filters)
        if not instruction:
            raise InstructionNotFoundError
        return instruction
