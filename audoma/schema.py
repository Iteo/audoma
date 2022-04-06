from drf_spectacular.contrib.django_filters import DjangoFilterExtension
from drf_spectacular.extensions import OpenApiFilterExtension
from rest_framework.filters import SearchFilter


class AudomaDjangoFilterExtension(DjangoFilterExtension):

    priority = 5

    def resolve_filter_field(
        self, auto_schema, model, filterset_class, field_name, filter_field
    ):
        if "choices" in filter_field.extra:
            filter_field.extra["help_text"] = filter_field.extra.get(
                "help_text", "{choices}"
            )
            filter_field.extra["help_text"] = filter_field.extra["help_text"].format(
                choices=self._generate_extra_choices_description(
                    filter_field, field_name
                )
            )
        return super().resolve_filter_field(
            auto_schema, model, filterset_class, field_name, filter_field
        )

    def _generate_extra_choices_description(self, filter_field, field_name):
        description = f"Filter by {field_name} \n"
        for key, val in filter_field.extra["choices"]:
            description += f" * `{key}` - {val}\n"
        return description


class SearchFilterExtension(OpenApiFilterExtension):
    target_class = SearchFilter

    SEARCH_PARAMS = {
        "^": "Starts-with search.",
        "=": "Exact matches.",
        "@": "Full-text search.",
        "$": "Regex search.",
    }

    def get_schema_operation_parameters(self, schema):
        view = schema.view
        result = self.target.get_schema_operation_parameters(view)[0]
        result["description"] = result.get("description", "{search_fields}")
        # overwrite default description
        if result["description"] == self.target_class.search_description:
            result["description"] = "{search_fields}"

        result["description"] = result["description"].format(
            search_fields=self._get_custom_serach_filter_description(view)
        )
        return [result]

    def _get_custom_serach_filter_description(self, view):
        description = "Search by: \n"
        processed_fields = self._get_processed_search_fields(view.search_fields)
        for field_name, field_description in processed_fields.items():
            description += f"* `{field_name}` \n" + "".join(field_description)
        return description

    def _get_processed_search_fields(self, fields):
        transformed_fields = {}
        fields = self._preprocess_fields(fields)

        while fields:
            start_phrase = fields[0].split("__")[0]
            processed_fields = [f for f in fields if f.startswith(start_phrase)]
            transformed_fields[start_phrase] = self._create_search_fields_description(
                processed_fields
            )
            fields = [f for f in fields if f not in processed_fields]

        return transformed_fields

    def _preprocess_fields(self, fields):
        for x, field in enumerate(fields):
            for keyword, description in self.SEARCH_PARAMS.items():
                if keyword in field:
                    fields[x] = field.replace(keyword, "")
                    fields[x] += f"({description})"
        return fields

    def _create_search_fields_description(self, fields):
        transformed_fields = []
        for field in fields:
            try:
                partials = field.split("__")
            except IndexError:
                transformed_fields.append(field)
                continue
            if len(partials) < 2:
                continue
            out = ""
            for x, partial in enumerate(partials[1:]):
                out += "\t " * (x + 1) + f"* `{partial}` \n"
            transformed_fields.append(out)
        return transformed_fields
