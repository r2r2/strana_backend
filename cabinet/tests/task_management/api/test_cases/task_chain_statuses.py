from typing import Any


class TaskChainStatusesCaseTestData:

    def get_statuses_case(self):
        test_cases: list[dict[str: Any]] = [
            dict(
                expected=[
                    {'name': 'test_task_group_status',
                     'priority': 1,
                     "color": "test_color",
                     'slug': 'test_slug',
                     "taskChain": {'name': 'test_task_chain'},
                     "statuses": [
                            {'name': 'test_task_status',
                             'description': 'test_description',
                             'type': {'value': 'test_type', 'label': None},
                             'priority': 1,
                             'slug': 'test_slug'},
                            {'name': 'test_task_status_2',
                             'description': 'test_description_2',
                             'type': {'value': 'test_type_2', 'label': None},
                             'priority': 1,
                             'slug': 'test_slug_2'}
                     ]
                     },
                ],
                status_code=200,
            ),
        ]

        return [
            (
                test_data['expected'],
                test_data['status_code'],
            ) for test_data in test_cases
        ]
