from typing import Any


class TaskChainStatusesCaseTestData:

    def get_statuses_case(self):
        test_cases: list[dict[str: Any]] = [
            dict(
                slug="test_slug_1",
                expected=[
                    {'name': 'test_name_1',
                     'description': 'test_description_1',
                     'type': {'value': 'test_type_1', 'label': None},
                     'priority': 1,
                     'slug': 'test_slug_1'},

                    {'name': 'test_name_2',
                     'description': 'test_description_2',
                     'type': {'value': 'test_type_2', 'label': None},
                     'priority': 2,
                     'slug': 'test_slug_2'}
                ],
                status_code=200,
            ),
            dict(
                slug="not_found_slug",
                expected={'message': 'Статус задания не найден', 'ok': False, 'reason': 'task_status_not_found'},
                status_code=404,
            ),
        ]

        return [
            (
                test_data['slug'],
                test_data['expected'],
                test_data['status_code'],
            ) for test_data in test_cases
        ]
