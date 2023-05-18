from collections import namedtuple

WrapperSpecsState = namedtuple(
    "WrapperState",
    [
        "class_",
        "repo",
        "labels_mapping",
        "specs_overrides",
        "range_fields",
        "choice_fields",
        "exclude_fields",
        "ordering_fields",
        "choices_serializer",
        "aliases",
        "choices",
        "ordering",
    ]
)
