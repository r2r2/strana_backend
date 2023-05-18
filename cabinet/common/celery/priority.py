from typing import Optional


class Priority:
    """
    Класс для приоритетов celery.
    """
    def __init__(self, steps: Optional[int] = 10):
        if steps < 3:
            raise ValueError('Steps arg must be > 3')
        self.__steps: list[int] = list(range(steps))

    @property
    def steps(self) -> list[int]:
        return self.__steps

    @property
    def highest(self) -> int:
        return self.__steps[0]

    @property
    def high(self) -> int:
        try:
            return self.__steps[self.highest + 1]
        except IndexError:
            return self.middle

    @property
    def middle(self) -> int:
        return self.__steps[len(self.__steps) // 2]

    @property
    def low(self) -> int:
        return self.__steps[self.lowest - 1]

    @property
    def lowest(self) -> int:
        return self.__steps[-1]
