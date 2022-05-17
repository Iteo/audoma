import re
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Type,
    Union,
)

from rest_framework.serializers import BaseSerializer

from django.urls import URLResolver
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

    possibilities = list(filter(lambda p: p.name == endpoint_name, new_patterns))
    if not possibilities:
        return
    # TODO - fix this before push
    # FIXME FIXME FIXME FIXME FIXME FIXME FIXME
    for p in possibilities:
        if "format" not in p.pattern.regex.pattern:
            return str(p.pattern)

    # different exception
    raise Exception


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

    # TODO - this does not make sense any more most probably
    def _process_link(
        self, link: Union[ChoicesOptionsLink, Dict[str, Any]]
    ) -> ChoicesOptionsLink:
        if isinstance(link, dict):
            link = ChoicesOptionsLink(**link)
        # TODO - maybe this should be silent?
        assert isinstance(link, ChoicesOptionsLink)

        # TODO does this make any sense at all?
        serializer = link.serializer_class()
        # serializer must own defined field
        assert serializer.fields.get(link.field_name, None) is not None
        return link

    # TODO - change typing
    def _create_link_title(self, link: ChoicesOptionsLink) -> str:
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
