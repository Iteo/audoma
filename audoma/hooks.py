from typing import (
    Callable,
    List,
    Tuple,
)

from django.conf import settings


def preprocess_include_path_format(
    endpoints: Tuple[str, str, str, Callable], **kwargs
) -> List[Tuple[str, str, str, Callable]]:
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
