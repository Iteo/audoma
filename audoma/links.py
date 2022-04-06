import re
from dataclasses import dataclass

from django.urls import reverse


@dataclass
class AudomaLink:

    link_name: str
    viewname: str
    method: str
    view_args: tuple = None
    view_kwargs: dict = None
    description: str = ""
    parameters: dict = None
    status_code: int = None

    method_mapping = {
        "get": "retrieve",
        "post": "create",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }

    def get_link_data(self, path_prefix, path_regex):
        path = reverse(
            self.viewname, args=self.view_args or (), kwargs=self.view_kwargs or {}
        )

        operationId = self._get_linked_operation_id(path, path_prefix, path_regex)
        self.parameters = self.parameters or {}
        return {
            "operationId": operationId,
            "parameters": self.parameters,
            "description": self.description,
        }

    def _get_linked_operation_id(self, path, path_prefix, path_regex):
        """override this for custom behaviour"""
        tokenized_path = self._tokenize_path(path, path_prefix)
        # replace dashes as they can be problematic later in code generation
        tokenized_path = [t.replace("-", "_") for t in tokenized_path]
        method_action = self.method_mapping[self.method.lower()]

        if not tokenized_path:
            tokenized_path.append("root")

        if re.search(r"<drf_format_suffix\w*:\w+>", path_regex):
            tokenized_path.append("formatted")
        return "_".join(tokenized_path + [method_action])

    def _tokenize_path(self, path, path_prefix):
        # remove path prefix
        path = re.sub(pattern=path_prefix, repl="", string=path, flags=re.IGNORECASE)
        # remove all view args and kwargs
        args = self.view_args + tuple(self.view_kwargs.values())
        for arg in args:
            path = path.replace(str(arg), "")

        # remove path variables
        path = re.sub(pattern=r"\{[\w\-]+\}", repl="", string=path)
        # cleanup and tokenize remaining parts.
        path = path.rstrip("/").lstrip("/").split("/")
        return [t for t in path if t]
