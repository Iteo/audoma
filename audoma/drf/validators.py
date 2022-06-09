from typing import (
    List,
    Tuple,
    Union,
)

from rest_framework import serializers
from rest_framework.validators import *  # noqa: F403, F401


class ExclusiveFieldsValidator:
    """
    This is extra validator defined in audoma.
    This validator allows to define mutually exclusvie fields.

    Attributes:
        fields - list or a tuple of mutually exclusive field names
        message - string validation error message
        required - boolean value, determines if fields are required
        message_reqiured - string message if one of fields is required and none has been passed

    Args:
        fields - list or a tuple of mutually exclusive field names
        message - string validation error message
        required - boolean value, determines if fields are required
        message_reqiured - string message if one of fields is required and none has been passed
    """

    message = "The fields {field_names} are mutually exclusive arguments."
    message_required = "One of the fields {field_names} is required."
    # requires_context = True

    def __init__(
        self,
        fields: Union[List[str], Tuple[str]],
        message: str = None,
        required: bool = True,
        message_required: str = None,
    ) -> None:
        self.fields = fields
        self.required = required
        if message:
            self.message = message
        if message_required:
            self.message_required = message_required

    def __call__(self, data: dict) -> None:
        in_data = sum(f in data for f in self.fields)
        if in_data > 1:
            raise serializers.ValidationError(
                self.message.format(field_names=", ".join(self.fields))
            )
        if in_data == 0 and self.required:
            raise serializers.ValidationError(
                self.message_required.format(field_names=", ".join(self.fields))
            )
