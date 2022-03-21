from django.conf import settings

from audoma.common_exceptions import CustomExceptionDescCreator


def preprocess_include_path_format(endpoints, **kwargs):
    """
    preprocessing hook that filters {format} prefdixed paths, in case
    schema pattern prefix is used and {format} path params are wanted.
    """

    format_path = settings.SCHEMA_PATTERN_PREFIX

    return [
        (path, path_regex, method, callback)
        for path, path_regex, method, callback in endpoints
        if (
            path.startswith(format_path)
            or path.startswith(format_path + "/")
            or path.startswith("/" + format_path)
        )
    ]


def postprocess_common_errors_section(result, **kwargs):
    generator = CustomExceptionDescCreator()
    result["info"] = result.get("info", {})
    result["info"]["description"] = (
        result["info"].get("description", "") + "\n\n" + generator.get_description()
    )

    return result
