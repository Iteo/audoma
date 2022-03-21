from rest_framework import exceptions

from django.conf import settings


WRAP_RESULT_SERIALIZER = getattr(settings, "AUDOMA_WRAP_RESULT_SERIALIZER", False)
settings.SPECTACULAR_SETTINGS[
    "GET_LIB_DOC_EXCLUDES"
] = "audoma.plumbing.get_lib_doc_excludes_audoma"


COMMON_API_ERRORS = [
    exceptions.NotFound(),
    exceptions.ValidationError(),
    exceptions.APIException(),
]

settings.SPECTACULAR_SETTINGS["POSTPROCESSING_HOOKS"] = [
    "audoma.hooks.postprocess_common_errors_section",
]

settings.SPECTACULAR_SETTINGS[
    "DEFAULT_GENERATOR_CLASS"
] = "audoma.generators.AudomaSchemaGenerator"
