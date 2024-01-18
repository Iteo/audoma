from typing import (
    NamedTuple,
    Tuple,
    Union,
)

from django_filters import rest_framework as df_filters

from audoma.plumbing import create_choices_enum_description


class DocumentedTypedChoiceFilter(df_filters.TypedChoiceFilter):
    """Extended TypedChoiceFilter to generate documentation automatically"""

    def _parse_choices(self, choices):
        if hasattr(choices, "get_api_choices"):
            return choices.get_api_choices()
        if isinstance(choices, dict):
            return choices
        if isinstance(choices, (list, tuple)):
            if isinstance(choices[0], (list, tuple)):
                return choices
            else:
                return tuple([(c, c) for c in choices])
        raise ValueError(f"Choices must be a dict, list or tuple, not {type(choices)}")

    def __init__(
        self, full_choices: Union[NamedTuple, Tuple], parameter_name: str, **kwargs
    ) -> None:
        self.parsed_choices = self._parse_choices(full_choices)
        if hasattr(full_choices, "get_value_by_name"):

            def coerce(value):
                return full_choices.get_value_by_name(value)

        else:

            def coerce(value):
                return dict(full_choices).get(value)

        super().__init__(
            coerce=coerce,
            choices=self.parsed_choices,
            **kwargs,
        )
        self.full_choices = full_choices
        self.parameter_name = parameter_name
        self.extra["help_text"] = self.extra.get("help_text", "{choices}").format(
            choices=create_choices_enum_description(
                self.parsed_choices, self.field_name
            )
        )
        self.extra["choices"] = self.parsed_choices
