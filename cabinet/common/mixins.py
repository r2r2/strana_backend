from typing import Union, Literal, Optional, Any
from .metas import ChoiceMeta
from .wrappers import classproperty


class Choices(metaclass=ChoiceMeta):
    """
    Common choices class that allows validating and serializing fields
    That define db_value and it's representative label
    Only fields that are defined as tuple may be used
    For further validating or serializing object
    Uses ChoiceMeta for it's creation and defines the logic explained below

    Correct example usage:

        class SomeConstant(mixins.Choices):
            CHOICE_ONE: str = "db_value_1", "Human representative label one"
            CHOICE_TWO: str = "db_value_2", "Human representative label two"

        Such class will provide following functionality:
            - Default declared fields will be replaced to it's zero position value
            e.g. SomeContact.CHOICE_ONE is "db_value_1"
            and SomeContact.CHOICE_TWO is "db_value_2"

            - Human readable labels will be moved to {choice_field_name}_LABEL
            attributes provided by metaclass logic
            e.g. CHOICE_ONE_LABEL is "Human representative label one"
            and CHOICE_TWO_LABEL is "Human representative label two"

            - You may get the value or label by it's pair related
            value using SomeConstant.to_value and SomeConstant.to_label methods

            - Declaring instance of this SomeConstant as pydantic.BaseModel field
            guides following rules:

                -- Use SomeConstant.validator to accept data: this will validate and accept
                only values, without label e.g. SomeConstant.CHOICE_ONE and SomeConstant.CHOICE_TWO

                -- Use SomeConstant.serializer to serialize data at response: this will be
                represented as dict with the following structure
                {"value" : SomeConstant.CHOICE_ONE, "label": SomeConstant.CHOICE_ONE_LABEL}

            - Comparing instances for equality | not equality uses direct access to instance value,
            e.g. SomeConstant(value=SomeConstant.CHOICE_ONE) == SomeConstant.CHOICE_ONE is True
            and SomeConstant(value=SomeConstant.CHOICE_ONE) != SomeConstant.CHOICE_TWO is True

            - Comparing class fields does not use overrided operator for equality and not equality

    Incorrect example usage:
        class SomeConstant(mixins.Choices):
            CHOICE_ONE: str = "db_value_1", "Human representative label one"
            CHOICE_TWO: int = 1, "Human representative label two"

        Logic defined by ChoiceMeta will raise a ValueError when declaring
        fields with different value types

    """

    def __init__(self, value: Optional[Union[int, str]] = None, label: Optional[str] = None):
        """
        Setting value and label by both or one of the arguments
        """
        self.value = None
        self.label = None
        if label is not None:
            self.value: Union[int, str, None] = self.to_value(label)
            self.label: str = label
        if value is not None:
            self.value: Union[int, str] = value
            self.label: Union[str, None] = self.to_label(value)
        if label is not None and value is not None:
            self.value: Union[int, str] = value
            self.label: str = label

    def __str__(self):
        result = self.value or "null"
        return str(result)

    @classmethod
    def to_label(cls, value: str) -> Union[str, None]:
        """
        Getting label from value
        """
        label: Optional[str] = None
        for name, val in cls.__dict__.items():
            if val == value:
                label: str = getattr(cls, f"{name}_LABEL")
        return label

    @classmethod
    def to_value(cls, label: str) -> Union[int, str, None]:
        """
        Getting value from label
        """
        value: Optional[str] = None
        for name, lbl in cls.__dict__.items():
            if lbl == label:
                value: Union[int, str] = getattr(cls, name.split("_")[0])
        return value

    @classproperty
    def validator(cls):
        """
        Pydantic validator
        """
        validator = Literal[0]
        validator.__args__ = tuple(cls.choices)
        return validator

    @classproperty
    def serializer(self):
        """
        Pydantic serializer
        """
        return Any

    def dict(self) -> dict[str, Any]:
        return dict(value=self.value, label=self.label)

    def __eq__(self, other: Any) -> bool:
        """
        Making sure value is compared
        """
        return self.value == other

    def __ne__(self, other) -> bool:
        """
        Making sure value is compared
        """
        return self.value != other


class ExceptionMixin:
    exception_class: Exception = Exception
