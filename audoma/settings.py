from django.conf import settings

WRAP_RESULT_SERIALIZER = getattr(settings, 'AUDOMA_WRAP_RESULT_SERIALIZER', False)
settings.SPECTACULAR_SETTINGS["GET_LIB_DOC_EXCLUDES"] = "audoma.plumbing.get_lib_doc_excludes_audoma"
