from dataclasses import dataclass

from rest_framework import (
    serializers,
    status,
)
from rest_framework.response import Response


class BaseBehaviourFactory:
    def create_behaviour(self, operation, operations):
        operation = operation or self._extract_collector(operations)

        if not operation:
            return None

        behaviour_kwargs = self._build_behaviour_kwargs
        return Behaviour(**behaviour_kwargs)

    def _extract_proper_operation(self, operations, request, code=None):
        ...

    # TODO - this should only return serializer_class, response specific class,
    # should be allowed to return error
    def _build_behaviour_kwargs(self, operation):
        if issubclass(operation, serializers.BaseSerializer):
            return {"serializer_class": operation}
        elif isinstance(operation, str):
            return {"error": operation}
        return {}


class CollectBehaviourFactory(BaseBehaviourFactory):
    def _extract_proper_operation(self, collectors, request, code=None):
        assert isinstance(collectors, dict)
        if not collectors:
            return

        method = request.method.lower()
        return collectors.get(method)


class ResponsesBehaviourFactory(BaseBehaviourFactory):
    def _extract_proper_operation(self, responses, request, code=None):
        assert isinstance(responses, dict)
        if not responses:
            return

        if isinstance(responses.keys()[0], str) and request:
            method = request.method.lower()
            responses = responses.get(method)
            if self.code:
                response = responses.get(code)
            return response

        elif isinstance(responses.keys[0], int) and code:
            response = responses.get(code)
            return response

        return None


@dataclass
class Behaviour:
    serializer_class: serializers.BaseSerializer
    error: str


def __apply_collect_behaviour(behaviour, request, instance):
    if not behaviour or not behaviour.serializer_class:
        return None

    if instance:
        serializer = behaviour.serializer_class(data=request.data, instance=instance)
    else:
        serializer = behaviour.serializer_class(data=request.data)
    serializer.is_valid()
    # TODO - This should me modified
    serializer.save()
    return serializer


def __apply_response_behaviour(behaviour, instance, code, view, collect_serializer):
    if behaviour.error:
        error = instance if isinstance(instance, str) else behaviour.error
        return Response(error, status_code=code)

    serializer_class = behaviour.serializer_class

    if collect_serializer:
        instance = collect_serializer.instance
        return_serializer = (
            serializer_class(instance)
            if serializer_class
            else view.get_result_serializer(instance)
        )
    else:
        return_serializer = (
            serializer_class() if serializer_class else view.get_result_serializer()
        )

    headers = view.get_success_headers(return_serializer.data)

    return Response(return_serializer.data, status=status.HTTP_200_OK, headers=headers)


def apply_behaviours(
    collect_behaviour, response_behaviour, instance, code, request, view
):
    # TODO add possibility to assign status code
    if not collect_behaviour and not response_behaviour:
        return view.perform_action(request, instance=instance)

    collect_serializer = __apply_collect_behaviour(collect_behaviour, request, instance)
    return __apply_response_behaviour(
        response_behaviour, instance, code, view, collect_serializer
    )
