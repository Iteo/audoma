import re
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Type,
    Union,
)

from drf_spectacular.plumbing import force_instance
from rest_framework.serializers import BaseSerializer

from django.urls import (
    NoReverseMatch,
    URLResolver,
)
from django.urls.resolvers import get_resolver


def get_endpoint_pattern(endpoint_name: str, urlconf=None) -> str:
    resolver = get_resolver(urlconf)
    patterns = resolver.url_patterns
    new_patterns = []
    resolvers = []

    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            resolvers.append(pattern)
            continue
        new_patterns.append(pattern)

    while resolvers:
        resolver = resolvers.pop()
        patterns = resolver.url_patterns
        for pattern in patterns:
            if isinstance(pattern, URLResolver):
                resolvers.append(pattern)
                continue
            new_patterns.append(pattern)

    possibilities = list(filter(lambda p: p.name == endpoint_name, new_patterns))

    for p in possibilities:
        if "format" not in p.pattern.regex.pattern:
            return str(p.pattern)

    raise NoReverseMatch(f"There is no pattern with name f{endpoint_name}")


@dataclass
class ChoicesOptionsLink:

    field_name: str
    viewname: str
    value_field: str
    display_field: str
    serializer_class: Type[BaseSerializer]

    description: str = ""

    def _format_param_field(self, field: str) -> str:
        if "$" in field:
            # than we presume that there has been given full pointer
            return field

        field = f"$response.body#results/*/{field}"

        return field

    @property
    def formatted_value_field(self) -> str:
        return self._format_param_field(self.value_field)

    @property
    def formatted_display_field(self) -> str:
        return self._format_param_field(self.display_field)

    def get_url_pattern(self) -> str:
        pattern = (
            get_endpoint_pattern(self.viewname)
            .replace("$", "")
            .replace("^", "/")
            .replace("/", "~1")
        )

        params = re.search(r"<.*>", pattern)
        if params:
            for param in params:
                param = param.string.replace("<", "{").replace(">", "}")

            regexes = re.search(r"\(.*\)", pattern)
            for x, regex in enumerate(regexes):
                pattern = pattern.replace(regex.string, params[x])

        pattern = f"#/paths/{pattern}"

        return pattern


class ChoicesOptionsLinkSchemaGenerator:
    def _process_link(
        self, link: Union[ChoicesOptionsLink, Dict[str, Any]]
    ) -> ChoicesOptionsLink:
        if isinstance(link, dict):
            link = ChoicesOptionsLink(**link)

        if not isinstance(link, ChoicesOptionsLink):
            raise TypeError(
                f"This is not possible to create ChoicesOptionsLink \
                    from object of type {type(link)}"
            )

        serializer = force_instance(link.serializer_class)
        # serializer must own defined field
        if not serializer.fields.get(link.field_name, None):
            raise AttributeError(
                f"Serializer class: {link.serializer_class} does not have field: {link.field_name}"
            )
        return link

    def _create_link_title(self, link: Union[ChoicesOptionsLink, dict]) -> str:
        partials = link.viewname.replace("-", " ").replace("_", " ").split(" ")
        partials = [p.capitalize() for p in partials]
        return " ".join(partials).title()

    def generate_schema(self, link: Union[ChoicesOptionsLink, Dict[str, Any]]) -> dict:
        if not link:
            return

        link = self._process_link(link)

        schema = {
            "operationRef": link.get_url_pattern(),
            # "parameters": "",
            "value": link.formatted_value_field,
            "display": link.formatted_display_field,
        }
        return schema
