from inspect import isclass

from rest_framework.serializers import BaseSerializer
from django.db.models import QuerySet
from rest_framework.response import Response



def extract_operation(operations, request, code=None, operation_category="response"):

    if isclass(operations) and issubclass(operations, BaseSerializer):
        return operations
    
    if operation_category == "response":
        return __extract_response_operation(operations, request, code)
    elif operation_category == "collect":
        return __extract_collect_operation(operations, request)
    else:
        raise ValueError("Unknown operation_category")


def __extract_response_operation(responses, request, code):
    assert isinstance(responses, dict)
    if not responses:
        return

    if isinstance(list(responses.keys())[0], str) and request:
        method = request.method.lower()
        response = responses.get(method)
        if code and isinstance(response, dict):
            response = responses.get(code)

        return response

    elif isinstance(list(responses.keys())[0], int) and code:
        response = responses.get(code)
        return response
    
    return None


def __extract_collect_operation(collectors, request):
    assert isinstance(collectors, dict)
    if not collectors:
        return 

    method = request.method.lower()
    return collectors.get(method)


def apply_response_operation(operation, instance, code, view, many):

    if isinstance(operation, str):
        instance = instance or operation
        instance = {'message': instance}
        return Response(instance, status=code) 
    
    if isinstance(operation, dict):
        instance = instance or operation.get(code)
        return Response(instance, status=code) 

    serializer_class = operation

    if instance:
        if isinstance(instance, QuerySet):
            serializer_kwargs = {'data': instance, 'many': many}
        else:
            serializer_kwargs = {'instance': instance, 'many': False}
    else:
        serializer_kwargs = {'many': many}
    return_serializer = serializer_class(**serializer_kwargs) if serializer_class else view.get_result_serializer(**serializer_kwargs)
    headers = view.get_success_headers(return_serializer.data)
    
    return Response(return_serializer.data, status=code, headers=headers)
