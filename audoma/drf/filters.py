from typing import (
    NamedTuple,
    Tuple,
    Union,
)

from django_filters import rest_framework as df_filters

from audoma.plumbing import create_choices_enum_description


class DocumentedTypedChoiceFilter(df_filters.TypedChoiceFilter):
    """Extended TypedChoiceFilter to generate documentation automatically"""

    def __init__(
        self, full_choices: Union[NamedTuple, Tuple], parameter_name: str, **kwargs
    ) -> None:
        self.parsed_choices = (
            full_choices.get_api_choices()
            if hasattr(full_choices, "get_choices")
            else full_choices
        )
        super().__init__(
            coerce=lambda value: full_choices.get_value_by_name(value),
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
