from django_filters import rest_framework as df_filters
from drf_yasg import openapi


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
        return openapi.Parameter(
            self.parameter_name, openapi.IN_QUERY,
            description=description,
            type=openapi.TYPE_STRING,
            enum=self.full_choices._fields
        )
