import pytest
from common.utils import partition_list


@pytest.mark.parametrize(
    "iterable,chunk_size,expected",
    [
        ([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),
        ([1, 2, 3, 4], 2, [[1, 2], [3, 4]]),
        ([1, 2], 3, [[1, 2]]),
    ],
)
def test_partition_list(client, iterable, chunk_size, expected) -> None:
    assert list(partition_list(iterable, chunk_size)) == expected
