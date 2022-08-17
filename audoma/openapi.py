import re
import typing
from copy import deepcopy
from inspect import isclass

from drf_spectacular.drainage import get_override
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import (
    ComponentRegistry,
    build_array_type,
    error,
    force_instance,
    sanitize_specification_extensions,
)
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse
from rest_framework.fields import Field
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import (
    AND,
    OR,
    BasePermission,
    OperandHolder,
    SingleOperandHolder,
)
from rest_framework.relations import RelatedField
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from django.views import View

from audoma.decorators import SerializersConfig
from audoma.drf.generics import GenericAPIView as AudomaGenericAPIView
from audoma.drf.serializers import BulkSerializerMixin
from audoma.drf.validators import ExclusiveFieldsValidator
from audoma.links import (
    ChoicesOptionsLink,
    ChoicesOptionsLinkSchemaGenerator,
)
from audoma.plumbing import create_choices_enum_description


class AudomaAutoSchema(AutoSchema):
    choice_link_schema_generator = ChoicesOptionsLinkSchemaGenerator()

    def _handle_permission(
        self,
        permission_class: typing.Union[
            OperandHolder, SingleOperandHolder, BasePermission
        ],
        operations: list,
        current_operation: typing.Type = AND,
    ) -> dict:
        permissions = {}

        if isinstance(permission_class, OperandHolder):
            if permission_class.operator_class == OR and current_operation != OR:
                operations.append("(")
            permissions.update(
                self._handle_permission(
                    permission_class.op1_class,
                    operations,
                    permission_class.operator_class,
                )
            )
            if permission_class.operator_class == OR:
                operations.append("|")
            elif permission_class.operator_class == AND:
                operations.append(" & ")
            permissions.update(
                self._handle_permission(
                    permission_class.op2_class,
                    operations,
                    permission_class.operator_class,
                )
            )
            if permission_class.operator_class == OR and current_operation != OR:
                operations.append(" )")
        elif isinstance(permission_class, SingleOperandHolder):
            permissions.update(
                self._handle_permission(
                    permission_class.op1_class,
                    operations,
                    permission_class.operator_class,
                )
            )

        else:
            try:
                permissions[permission_class.__name__] = (
                    permission_class.get_description(self.view),
                )
            except AttributeError:
                if permission_class.__doc__:
                    permissions[
                        permission_class.__name__
                    ] = permission_class.__doc__.replace("\n", " ").strip()
                else:
                    permissions[
                        permission_class.__name__
                    ] = "(No description for this permission)"
            operations.append(f"`{permission_class.__name__}`")

        return permissions

    def _get_permissions_description(self) -> str:
        permissions = {}
        operations = []

        for permission_class in getattr(self.view, "permission_classes", []):
            if operations:
                operations.append("&")
            permissions.update(self._handle_permission(permission_class, operations))

        if permissions:
            return (
                "\n\n**Permissions:**\n"
                + " ".join(operations)
                + "\n"
                + "\n".join(
                    f"+ `{name}`: *{doc_str}*" for name, doc_str in permissions.items()
                )
            )
        else:
            return ""

    def get_description(self) -> str:
        description = super().get_description() or ""
        description += self._get_permissions_description()
        return description

    def _extract_action_function(self, view) -> typing.Callable:
        action = getattr(view, "action", None)
        if not action:
            return

        return getattr(view, action, None)

    def _parse_action_result_serializer(
        self,
        serializer: typing.Union[typing.Type[BaseSerializer], str],
        many: bool = False,
    ) -> typing.Union[BaseSerializer, str]:
        if isinstance(serializer, str):
            return OpenApiResponse(description=serializer)
        elif isclass(serializer) and issubclass(serializer, BaseSerializer):
            print(many, serializer)
            return serializer(many=many)
        return serializer

    def _parse_action_result_serializers(
        self, action_serializers: SerializersConfig, many: bool = False
    ) -> typing.Union[
        typing.Dict[str, OpenApiResponse],
        typing.Dict[str, BaseSerializer],
        typing.Dict[str, typing.Dict[int, BaseSerializer]],
    ]:
        if not action_serializers:
            return action_serializers

        if isinstance(action_serializers, str):
            return {"default": OpenApiResponse(description=action_serializers)}

        if not isinstance(action_serializers, dict):
            action_serializer = self._parse_action_result_serializer(
                action_serializers, many=many
            )
            return {"default": action_serializer}

        parsed_action_serializers = deepcopy(action_serializers)

        for method, method_serializers in action_serializers.items():
            if isinstance(method_serializers, dict):
                for code, item in method_serializers.items():
                    parsed_action_serializers[method][
                        code
                    ] = self._parse_action_result_serializer(item, many=many)
            else:
                parsed_action_serializers[
                    method
                ] = self._parse_action_result_serializer(method_serializers, many=many)

        return parsed_action_serializers

    def _parse_action_errors(self, action_errors) -> typing.Dict[int, OpenApiResponse]:
        if not action_errors:
            return action_errors

        parsed_errors = {}
        for err in action_errors:
            if isclass(err):
                err = err()

            # build properties
            properties = {}
            for key, value in vars(err).items():
                properties[key] = {key: {"type": type(value).__name__}}

            parsed_errors[err.status_code] = OpenApiResponse(
                response={
                    "type": "object",
                    "properties": properties,
                    "example": vars(err),
                }
            )
        return parsed_errors

    def _extract_audoma_action_operations(
        self, view: View, serializer_type: str
    ) -> typing.Union[
        typing.Dict[str, OpenApiResponse],
        typing.Dict[str, BaseSerializer],
        typing.Dict[str, typing.Type[BaseSerializer]],
        typing.Dict[str, typing.Dict[int, BaseSerializer]],
        typing.Dict[int, OpenApiResponse],
    ]:
        """
        Extracts the audoma action operations from the view
        """
        action_function = self._extract_action_function(view)
        _audoma = getattr(action_function, "_audoma", None)
        many = action_serializers = getattr(_audoma, "many", False)
        if not _audoma:
            return {}

        if serializer_type == "collect":
            action_serializers = getattr(_audoma, "collectors", None)
        else:
            results = self._parse_action_result_serializers(
                getattr(_audoma, "results", None), many
            )
            errors = self._parse_action_errors(getattr(_audoma, "errors", {}))
            if results:
                action_serializers = results
                action_serializers.update(errors)
            else:
                action_serializers = errors

        return action_serializers

    def _get_serializer(  # noqa: C901
        self, serializer_type: str = "collect"
    ) -> typing.Union[BaseSerializer, typing.Type[BaseSerializer]]:
        view = self.view
        method = view.request.method

        action_serializers = self._extract_audoma_action_operations(
            view, serializer_type
        )

        if action_serializers:
            if (
                isinstance(action_serializers, dict)
                and method.lower() in action_serializers
            ):
                return action_serializers[method.lower()]
            else:
                return action_serializers

        try:
            if isinstance(view, AudomaGenericAPIView):
                return view.get_serializer_class(type=serializer_type)()
            elif isinstance(view, GenericAPIView):
                # try to circumvent queryset issues with calling get_serializer. if view has NOT
                # overridden get_serializer, its safe to use get_serializer_class.
                if view.__class__.get_serializer == GenericAPIView.get_serializer:
                    return view.get_serializer_class()()
                return view.get_serializer()
            elif isinstance(view, APIView):
                # APIView does not implement the required interface, but be lenient and make
                # good guesses before giving up and emitting a warning.
                if callable(getattr(view, "get_serializer", None)):
                    return view.get_serializer()
                elif callable(getattr(view, "get_serializer_class", None)):
                    return view.get_serializer_class()()
                elif hasattr(view, "serializer_class"):
                    return view.serializer_class
                else:
                    error(
                        "unable to guess serializer. This is graceful "
                        "fallback handling for APIViews. Consider using GenericAPIView as view base "
                        "class, if view is under your control. Ignoring view for now. "
                    )
            else:
                error(
                    "Encountered unknown view base class. Please report this issue. Ignoring for now"
                )
        except Exception as exc:
            error(
                f"exception raised while getting serializer. Hint: "
                f"Is get_serializer_class() returning None or is get_queryset() not working without "
                f"a request? Ignoring the view for now. (Exception: {exc})"
            )

    def get_response_serializers(
        self,
    ) -> typing.Union[BaseSerializer, typing.Type[BaseSerializer]]:
        """overrides this for custom behaviour"""
        return self._get_serializer(serializer_type="result")

    def _get_enum_choices_for_field(self, field):
        if hasattr(field, "original_choices"):
            choices = field.original_choices
        else:
            choices = field.choices

        if hasattr(choices, "items"):
            choices = choices.items()

        return {"choices": {key: value for key, value in choices}}

    def _get_link_choices_for_field(self, field, serializer):
        link = serializer.choices_options_links.get(field.field_name, None)
        if not link:
            return

        if isinstance(link, dict):
            # presume that this dictionary are link kwargs
            link.update(
                {"field_name": field.field_name, "serializer_class": type(serializer)}
            )
            link = ChoicesOptionsLink(**link)

        choices = self.choice_link_schema_generator.generate_schema(link)
        if choices:
            if link.field_name == field.field_name:
                return choices
        return

    def _map_serializer_field(
        self, field: Field, direction: str, bypass_extensions=False
    ) -> dict:
        """
        Allows to use @extend_schema_field with `field` dict so that
        it gets updated instead of being overriden
        """
        serializer_type = "collect" if direction == "request" else "result"
        serializer = self._get_serializer(serializer_type=serializer_type)
        serializer = force_instance(serializer)

        if (
            hasattr(serializer, "Meta")
            and self.is_bulk
            and field.field_name == getattr(serializer.Meta, "id_field", None)
        ):
            field.read_only = False
            field.required = True

        has_annotation = (
            hasattr(field, "_spectacular_annotation")
            and "field" in field._spectacular_annotation
            and isinstance(field._spectacular_annotation["field"], dict)
        )
        if has_annotation:
            annotation = field._spectacular_annotation
            field._spectacular_annotation = {}

        result = super()._map_serializer_field(
            field, direction, bypass_extensions=bypass_extensions
        )

        if not isinstance(field, RelatedField) and hasattr(field, "choices"):
            result["x-choices"] = self._get_enum_choices_for_field(field)
            result["description"] = create_choices_enum_description(
                result["x-choices"]["choices"], field.field_name
            )

        if hasattr(serializer, "choices_options_links"):
            choices = self._get_link_choices_for_field(field, serializer)
            if choices:
                result["x-choices"] = choices

        if has_annotation:
            result.update(annotation["field"])
        return result

    def _get_request_for_media_type(self, serializer):

        schema, request_body_required = super()._get_request_for_media_type(serializer)
        if self.is_bulk:
            schema = build_array_type(schema)
        if isinstance(serializer, BulkSerializerMixin) and self.view.action == "create":
            schema = {"oneOf": [build_array_type(schema), schema]}
        return schema, request_body_required

    def _get_response_for_code(self, serializer, status_code, media_types=None):

        schema_resp = super()._get_response_for_code(
            serializer, status_code, media_types
        )

        if self.is_bulk:
            for media_type in schema_resp["content"]:
                schema = schema_resp["content"][media_type]["schema"]
                schema_resp["content"][media_type]["schema"] = build_array_type(schema)

        if isinstance(serializer, BulkSerializerMixin) and self.view.action == "create":
            for media_type in schema_resp["content"]:
                schema = schema_resp["content"][media_type]["schema"]
                schema_resp["content"][media_type]["schema"] = {
                    "oneOf": [build_array_type(schema), schema]
                }
        return schema_resp

    def _build_exclusive_fields_schema(
        self, schema: dict, exclusive_fields: typing.List[str]
    ) -> typing.List[dict]:
        modified_schemas = []
        for field in exclusive_fields:
            new_schema = deepcopy(schema)
            new_schema["properties"].pop(field)
            modified_schemas.append(new_schema)
        return modified_schemas

    def _map_serializer(
        self,
        serializer: typing.Union[
            OpenApiTypes, BaseSerializer, typing.Type[BaseSerializer]
        ],
        direction: str,
        bypass_extensions: bool = False,
    ) -> dict:
        serializer = force_instance(serializer)
        serializer_extension = OpenApiSerializerExtension.get_match(serializer)

        if serializer_extension and not bypass_extensions:
            schema = serializer_extension.map_serializer(self, direction)
        else:
            schema = self._map_basic_serializer(serializer, direction)

        if hasattr(serializer, "validators") and direction == "request":
            subschemas = []
            for validator in serializer.validators:
                if isinstance(validator, ExclusiveFieldsValidator):
                    subschemas += self._build_exclusive_fields_schema(
                        schema, validator.fields
                    )

            if subschemas:
                schema = {"oneOf": subschemas}

        extensions = get_override(serializer, "extensions", {})
        if extensions:
            schema.update(sanitize_specification_extensions(extensions))

        return self._postprocess_serializer_schema(schema, serializer, direction)

    def get_operation_id(self):
        """override this for custom behaviour"""
        tokenized_path = self._tokenize_path()

        if self.is_bulk:
            tokenized_path.append("bulk")

        # replace dashes as they can be problematic later in code generation
        tokenized_path = [t.replace("-", "_") for t in tokenized_path]

        if self.method == "GET" and self._is_list_view():
            action = "list"
        else:
            action = self.method_mapping[self.method.lower()]

        if not tokenized_path:
            tokenized_path.append("root")

        if re.search(r"<drf_format_suffix\w*:\w+>", self.path_regex):
            tokenized_path.append("formatted")

        return "_".join(tokenized_path + [action])

    def get_operation(
        self, path, path_regex, path_prefix, method, registry: ComponentRegistry
    ):
        self.is_bulk = False

        if "bulk" in getattr(self.view, "action", "") and method in [
            "POST",
            "PUT",
            "PATCH",
        ]:
            self.is_bulk = True

        return super().get_operation(path, path_regex, path_prefix, method, registry)
