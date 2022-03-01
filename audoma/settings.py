from django.conf import settings

WRAP_RESULT_SERIALIZER = getattr(settings, 'AUDOMA_WRAP_RESULT_SERIALIZER', False)
