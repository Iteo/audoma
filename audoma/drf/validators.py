from rest_framework import serializers
from rest_framework.validators import *  # noqa: F403, F401


class ExclusiveFieldsValidator:
    message = "The fields {field_names} are mutually exclusive arguments."
    message_required = "One of the fields {field_names} is required."
    # requires_context = True

    def __init__(self, fields, message=None, required=True, message_required=None):
        self.fields = fields
        self.required = required
        if message:
            self.message = message
        if message_required:
            self.message_required = message_required

    def __call__(self, data):
        in_data = sum(f in data for f in self.fields)
        if in_data > 1:
            raise serializers.ValidationError(
                self.message.format(field_names=", ".join(self.fields))
            )
        if in_data == 0 and self.required:
            raise serializers.ValidationError(
                self.message_required.format(field_names=", ".join(self.fields))
            )
