import random

import exrex

from django.core import validators


class DEFAULT:
    pass


class Example:
    def __init__(self, field, example=DEFAULT):
        self.field = field
        self.example = example

    def generate_value(self):
        return DEFAULT

    def get_value(self):
        if self.example is not DEFAULT:
            if callable(self.example):
                return self.example()
            return self.example
        return self.generate_value()

    def to_representation(self, value):
        return self.field.to_representation(value)


class NumericExample(Example):
    def generate_value(self):
        min_val = getattr(self.field, "min_value", 1) or 1
        max_val = getattr(self.field, "max_value", 1000) or 1000
        return random.uniform(min_val, max_val)


class RegexExample(Example):
    def generate_value(self):
        regex_validators = [
            validator
            for validator in self.field.validators
            if isinstance(validator, validators.RegexValidator)
        ]
        if regex_validators:
            regex_validator = regex_validators[0]
            return exrex.getone(regex_validator.regex.pattern)
        return None
