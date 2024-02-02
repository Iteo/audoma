import datetime
import random
from decimal import Decimal
from typing import (
    Any,
    Type,
)

import exrex

from django.core import validators


class DEFAULT:
    pass


class Example:
    """
    Class that represents an example for a field.
    It allows to add example to the field during initialization.
    """

    def __init__(self, field, example=DEFAULT) -> None:
        self.field = field
        self.example = example

    def generate_value(self) -> Type[DEFAULT]:
        return DEFAULT

    def get_value(self) -> Any:
        if self.example is not DEFAULT:
            if callable(self.example):
                return self.example()
            return self.example
        return self.generate_value()

    def to_representation(self, value) -> Any:
        return self.field.to_representation(value)


class NumericExample(Example):
    def generate_value(self) -> float:
        """
        Extracts information from the field and generates a random value
        based on min_value and max_value.

        Returns:
            Random value between min_value and max_value
        """
        min_val = float(getattr(self.field, "min_value", 1) or 1)
        max_val = float(getattr(self.field, "max_value", 1000) or 1000)
        decimal_places = getattr(self.field, "decimal_places", None)
        if decimal_places:
            fmt = f".{decimal_places}f"
            return Decimal(f"{(max_val):{fmt}}")
        ret = random.uniform(min_val, max_val)
        return ret


class RegexExample(Example):
    def generate_value(self) -> str:
        """
        Extracts information from the field and generates a random value
        based on field's  RegexValidators.

        Returns:
            Generated regex string if regex is found, otherwise returns None
        """
        regex_validators = [
            validator
            for validator in self.field.validators
            if isinstance(validator, validators.RegexValidator)
        ]
        if regex_validators:
            regex_validator = regex_validators[0]
            return exrex.getone(regex_validator.regex.pattern)
        return None


class _DateRelatedExampleMixin:
    def generate_value(self) -> datetime.datetime:
        return datetime.datetime.now() - datetime.timedelta(
            days=random.randint(0, 20),
            hours=random.randint(0, 10),
            minutes=random.randint(0, 40),
        )


class DateExample(_DateRelatedExampleMixin, Example):
    def generate_value(self) -> datetime.date:
        return super().generate_value().date()


class TimeExample(_DateRelatedExampleMixin, Example):
    def generate_value(self) -> datetime.date:
        return super().generate_value().time()


class DateTimeExample(_DateRelatedExampleMixin, Example):
    ...


class Base64Example(Example):
    def generate_value(self) -> float:
        """
        Extracts information from the field and generates a random value
        based on min_value and max_value.

        Returns:
            Random value between min_value and max_value
        """
        max_length = float(getattr(self.field, "max_length", 1) or 1)
        length = max_length
        return "%030x" % random.randrange(16**length)


class RangeExample(Example):
    def generate_value(self) -> float:
        """
        Extracts information from the field and generates a random value
        based on min_value and max_value.

        Returns:
            Random value between min_value and max_value
        """
        child_field = getattr(self.field, "child", None)
        example_class = (
            child_field.audoma_example_class
            if child_field is not None
            else NumericExample
        )
        lower, upper = (
            example_class(field=child_field).generate_value(),
            example_class(field=child_field).generate_value(),
        )
        lower, upper = (upper, lower) if lower > upper else (lower, upper)
        return {"lower": lower, "upper": upper}
