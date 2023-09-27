from uuid import UUID, uuid4

import pytest
from app import app

from litestar.testing import TestClient

inputs = [
    [1, 2, 3],
    ['a', 'b', 'c'],
    [uuid4(), uuid4(), uuid4()],
]

outputs = [{'ids': _input} for _input in inputs]


# all scenarios fail with
#
# {
#     'extra': [
#         {
#             'key': 'ids',
#             'message': 'Expected `array | null`, got `str`',
#             'source': 'query',
#         }
#     ],
# }
@pytest.mark.parametrize('ids, expected', zip(inputs, outputs))
def test_id_list(ids: list[int] | list[str] | list[UUID], expected: dict) -> None:
    with TestClient(app=app) as client:
        data = client.get('', params={'ids': ids}).json()
        assert data == expected


# passes
def test_id_list__no_ids_passed() -> None:
    with TestClient(app=app) as client:
        data = client.get('').json()
        assert data == {'ids': []}
