import random
from typing import (
    Any,
    Type,
)

import exrex

from django.core import validators


class DEFAULT:
    pass


class Example:
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
        min_val = getattr(self.field, "min_value", 1) or 1
        max_val = getattr(self.field, "max_value", 1000) or 1000
        return random.uniform(min_val, max_val)


class RegexExample(Example):
    def generate_value(self) -> str:
        regex_validators = [
            validator
            for validator in self.field.validators
            if isinstance(validator, validators.RegexValidator)
        ]
        if regex_validators:
            regex_validator = regex_validators[0]
            return exrex.getone(regex_validator.regex.pattern)
        return None
