from inspect import isclass
from typing import (
    Callable,
    List,
    Tuple,
)

from rest_framework.settings import api_settings

from django.conf import settings as project_settings
from django.utils.module_loading import import_string

from audoma import settings as audoma_settings


def preprocess_include_path_format(
    endpoints: Tuple[str, str, str, Callable], **kwargs
) -> List[Tuple[str, str, str, Callable]]:
    """
    Preprocessing hook that filters {format} prefdixed paths, in case
    schema pattern prefix is used and {format} path params are wanted.
    """
    format_path = project_settings.SCHEMA_PATTERN_PREFIX

    return [
        (path, path_regex, method, callback)
        for path, path_regex, method, callback in endpoints
        if (
            path.startswith(format_path)
            or path.startswith(format_path + "/")
            or path.startswith("/" + format_path)
        )
    ]


def postprocess_common_errors_section(result: dict, request, **kwargs) -> dict:
    """
    Postprocessing hook which adds COMMON_API_ERRORS description to the API description.
    """
    common_exceptions = audoma_settings.COMMON_API_ERRORS + getattr(
        project_settings, "COMMON_API_ERRORS", []
    )

    renderer = project_settings.REST_FRAMEWORK.get(
        "DEFAULT_RENDERER_CLASSES", api_settings.DEFAULT_RENDERER_CLASSES
    )[0]

    if not callable(renderer):
        renderer = import_string(renderer)

    renderer = renderer()

    def generate_exception_desc(error):
        exc_desc = ""
        exc_desc = f"Status Code: `{error.status_code}` \n\n"
        rendered_error_data = renderer.render(
            data=vars(error), renderer_context={"indent": 4}
        ).decode("utf-8")

        exc_desc += f"``` \n {rendered_error_data} \n ``` \n\n"
        return exc_desc

    result["info"] = result.get("info", {})

    description = "###  Common API Errors \n"
    for error in common_exceptions:
        if isclass(error):
            error = error()
        description += generate_exception_desc(error)

    result["info"]["description"] = (
        result["info"].get("description", "") + "\n\n" + description
    )

    return result
