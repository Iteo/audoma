from rest_framework.settings import api_settings

from django.conf import settings as project_settings

from audoma import settings as audoma_settings


def preprocess_include_path_format(endpoints, **kwargs):
    """
    preprocessing hook that filters {format} prefdixed paths, in case
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


def postprocess_common_errors_section(result, request, **kwargs):
    """
    Postprocessing hook which adds COMMON_API_ERRORS description to the API description.
    """
    common_exceptions = (
        audoma_settings.COMMON_API_ERRORS + project_settings.COMMON_API_ERRORS or []
    )

    renderer = project_settings.REST_FRAMEWORK.get(
        "DEFAULT_RENDERER_CLASSES", api_settings.DEFAULT_RENDERER_CLASSES
    )[0]()

    def _get_description():
        desc = "###  Common API Errors \n"
        for error in common_exceptions:
            desc += __generate_exception_desc(error)
        return desc

    def __generate_exception_desc(error):
        exc_desc = ""
        exc_desc = f"Status Code: `{error.status_code}` \n\n"
        rendered_error_data = renderer.render(
            data=error.__dict__, renderer_context={"indent": 4}
        ).decode("utf-8")

        exc_desc += f"``` \n {rendered_error_data} \n ``` \n\n"
        return exc_desc

    result["info"] = result.get("info", {})
    result["info"]["description"] = (
        result["info"].get("description", "") + "\n\n" + _get_description()
    )

    return result
