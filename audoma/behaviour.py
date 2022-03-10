from dataclasses import dataclass

from rest_framework import (
    serializers,
    status,
)
from rest_framework.response import Response


class BaseBehaviourFactory:
    def create_behaviour(self, operation, operations, request, code):
        operation = operation or self._extract_proper_operation(operations, request, code)

        if not operation:
            return None
        
        behaviour_kwargs = self._build_behaviour_kwargs(operation, code)
        return Behaviour(**behaviour_kwargs)

    def _extract_proper_operation(self, operations, request, code=None):
        ...

    def _build_behaviour_kwargs(self, operation, code):
        if not isinstance(operation, type):
            return {}

        if issubclass(operation, serializers.BaseSerializer):
            return {'serializer_class': operation}
        return {}


class CollectBehaviourFactory(BaseBehaviourFactory):
    def _extract_proper_operation(self, collectors, request, code=None):
        assert isinstance(collectors, dict)
        if not collectors:
            return

        method = request.method.lower()
        return collectors.get(method)


class ResponsesBehaviourFactory(BaseBehaviourFactory):
    
    def _build_behaviour_kwargs(self, operation, code):
        kwargs = super()._build_behaviour_kwargs(operation, code)
        if isinstance(operation, str):
            kwargs.update({'error_message': operation})
        elif isinstance(operation, dict):
            kwargs.update({'error_message': operation.get(code, None)})

        return kwargs

    def _extract_proper_operation(self, responses, request, code=None):
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


@dataclass
class Behaviour:
    serializer_class: serializers.BaseSerializer = None
    error_message: str = None


def __apply_collect_behaviour(behaviour, request, instance):
    if not behaviour or not behaviour.serializer_class:
        return None

    if instance:
        serializer = behaviour.serializer_class(data=request.data, instance=instance)
    else:
        serializer = behaviour.serializer_class(data=request.data)
    serializer.is_valid()
    # TODO - This should me modified
    # NOTE - there should be possibility to pass param which defined serializer execution method
    serializer.save()
    return serializer

def __apply_response_behaviour(behaviour, request, code, view, instance):

    if behaviour.error_message:
        return Response(behaviour.error_message, status=code) 

    serializer_class = behaviour.serializer_class

    if instance:
        return_serializer = serializer_class(instance) if serializer_class else view.get_result_serializer(instance)
    else:
        return_serializer = (
            serializer_class() if serializer_class else view.get_result_serializer()
        )

    headers = view.get_success_headers(return_serializer.data)

    return Response(return_serializer.data, status=code, headers=headers)


def apply_behaviours(
    collect_behaviour, response_behaviour, instance, code, request, view
):
    # TODO add possibility to assign status code
    if not collect_behaviour and not response_behaviour:
        return view.perform_action(request, instance=instance, status=code)

    collect_serializer = __apply_collect_behaviour(collect_behaviour, request, instance)

    # TODO - clean this code
    instance = collect_serializer.instance if collect_serializer else instance

    # if other error message defined, set behaviour error message to this message
    response_behaviour.error_message = instance if isinstance(instance, str) else response_behaviour.error_message

    return __apply_response_behaviour(response_behaviour, request, code, view, instance)
