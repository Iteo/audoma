from rest_framework import exceptions

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404


WRAP_RESULT_SERIALIZER = getattr(settings, "AUDOMA_WRAP_RESULT_SERIALIZER", False)
settings.SPECTACULAR_SETTINGS[
    "GET_LIB_DOC_EXCLUDES"
] = "audoma.plumbing.get_lib_doc_excludes_audoma"


COMMON_API_ERRORS = [
    exceptions.NotFound,
    exceptions.NotAuthenticated,
    exceptions.AuthenticationFailed,
    exceptions.ParseError,
    exceptions.PermissionDenied,
    exceptions.NotAcceptable,
    exceptions.ValidationError,
    exceptions.Throttled,
    Http404,
    PermissionDenied,
]

settings.SPECTACULAR_SETTINGS["POSTPROCESSING_HOOKS"] = [
    "audoma.hooks.postprocess_common_errors_section",
]
