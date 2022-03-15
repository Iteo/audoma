from django_filters import rest_framework as df_filters


class DocumentedTypedChoiceFilter(df_filters.TypedChoiceFilter):
    """Extended TypedChoiceFilter to generate documentation automatically"""

    def __init__(self, full_choices, parameter_name, **kwargs):
        super().__init__(
            coerce=lambda value: full_choices.get_value_by_name(value),
            choices=full_choices.get_api_choices(),
            **kwargs,
        )
        self.full_choices = full_choices
        self.parameter_name = parameter_name
        self.extra['help_text'] = self.extra.get('help_text', "") + "<br/>"
        self.extra['help_text'] += self._get_choices_description()

    def _get_choices_description(self):
        description = f"Filter by {self.parameter_name} \n"
        for key, val in self.full_choices.get_api_choices():
                description += f" * `{key}` - {val}\n"
        return description
