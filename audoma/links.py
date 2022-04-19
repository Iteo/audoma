import urllib
from dataclasses import dataclass
from typing import Dict

from rest_framework.serializers import BaseSerializer

from django.urls import reverse


@dataclass
class AudomaOptionsLink:

    viewname: str
    sources: Dict[str, str] = None
    destinations: Dict[str, str] = None
    detail: bool = True
    view_kwargs: dict = None
    description: str = ""
    method: str = "get"

    def _format_param_field(self, fieldname):
        if "$" in fieldname:
            return fieldname
        return f"$response.body#/{fieldname}"

    def __post_init__(self, *args, **kwargs):
        self.view_kwargs = self.view_kwargs or {}
        self.sources = self.sources or {}
        self.destinations = self.destinations or {}

    @property
    def formatted_destinations(self):
        return {
            key: self._format_param_field(value)
            for key, value in self.destinations.items()
        }

    @property
    def formatted_sources(self):
        return {
            key: self._format_param_field(value) for key, value in self.sources.items()
        }

    def get_reversed_link(self) -> str:
        view_kwargs = self.view_kwargs
        view_kwargs.update(
            {key: "{" + value + "}" for key, value in self.destinations.items()}
        )

        return reverse(self.viewname, kwargs=view_kwargs)


class AudomaOptionsLinkSchemaGenerator:
    def __init__(self, serializer: BaseSerializer):
        self.serializer = serializer
        self._audoma_links = serializer.get_audoma_links()

    def _generate_param_schema(self, link: AudomaOptionsLink) -> dict:
        schema = {}
        schema.update(link.formatted_destinations)
        schema.update(link.formatted_sources)
        return schema

    def _get_link_schema(self, audoma_link: AudomaOptionsLink) -> dict:
        path = urllib.parse.unquote(audoma_link.get_reversed_link())

        return {
            "operationRef": path,
            "description": audoma_link.description,
            "parameters": self._generate_param_schema(audoma_link),
        }

    def _create_link_title(self, link: AudomaOptionsLink) -> str:
        partials = link.viewname.replace("-", " ").replace("_", " ").split(" ")
        partials = [p.capitalize() for p in partials]
        return " ".join(partials).title()

    def generate_schema(self) -> dict:
        audoma_links = {}
        for item in self._audoma_links:
            link = item.get("link", None)
            if not link:
                continue
            title = self._create_link_title(link)
            audoma_links[title] = self._get_link_schema(link)
        return audoma_links
