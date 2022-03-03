from django_filters import rest_framework as df_filters
from drf_spectacular.utils import OpenApiParameter


class DocumentedTypedChoiceFilter(df_filters.TypedChoiceFilter):
    """Extended TypedChoiceFilter to generate documentation automatically"""

    def __init__(self, full_choices, parameter_name, **kwargs):
        super().__init__(
            coerce=lambda value: full_choices.get_value_by_name(value),
            choices=full_choices.get_api_choices(),
            **kwargs
        )
        self.full_choices = full_choices
        self.parameter_name = parameter_name

    def create_openapi_description(self):
        choices = self.full_choices.get_api_choices()
        description = "Filter by {}\n".format(self.parameter_name)
        for key, val in choices:
            description += f" * `{key}` - {val}\n"

        return OpenApiParameter(
            name=self.parameter_name,
            description=description,
            enum=self.full_choices._fields
        )
