from dataclasses import dataclass

from rest_framework import serializers, status
from rest_framework.response import Response



def extract_operation(operation, operations, request, code=None, operation_category="response"):
    if operation_category == "response":
        return operation or __extract_response_operation(operations, request, code)
    elif operation_category == "collect":
        return operation or _extract_collect_operation(operations, request)
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


def _extract_collect_operation(collectors, request):
    assert isinstance(collectors, dict)
    if not collectors:
        return 

    method = request.method.lower()
    return collectors.get(method)


def apply_response_operation(operation, instance, code, request, view):
    if isinstance(operation, str):
        instance = instance or operation
        return Response(instance, status=code) 
    
    if isinstance(operation, dict):
        instance = instance or operation.get(code)
        return Response(instance, status=code) 

    serializer_class = operation
    if instance:
        return_serializer = serializer_class(instance) if serializer_class else view.get_result_serializer(instance)
    else:
        return_serializer = serializer_class() if serializer_class else view.get_result_serializer()

    headers = view.get_success_headers(return_serializer.data)

    return Response(return_serializer.data, status=code, headers=headers)
