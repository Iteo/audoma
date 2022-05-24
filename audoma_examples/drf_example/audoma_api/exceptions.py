from rest_framework import status
from rest_framework.exceptions import APIException


class CustomBadRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Custom Bad Request Exception"


class CustomConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict has occured"
