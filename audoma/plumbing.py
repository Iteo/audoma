from typing import (
    List,
    Tuple,
    Type,
    Union,
)

from drf_spectacular.drainage import cache
from rest_framework import (
    generics,
    mixins,
    serializers,
    views,
    viewsets,
)

from audoma.drf import (
    generics as audoma_generics,
    mixins as audoma_mixins,
    serializers as audoma_serializers,
    viewsets as audoma_viewsets,
)


@cache
def get_lib_doc_excludes_audoma() -> List[Type]:

    return [
        views.APIView,
        *[
            getattr(serializers, c)
            for c in dir(serializers)
            if c.endswith("Serializer")
        ],
        *[getattr(viewsets, c) for c in dir(viewsets) if c.endswith("ViewSet")],
        *[getattr(generics, c) for c in dir(generics) if c.endswith("APIView")],
        *[getattr(mixins, c) for c in dir(mixins) if c.endswith("Mixin")],
        *[
            getattr(audoma_viewsets, c)
            for c in dir(audoma_viewsets)
            if c.endswith("ViewSet")
        ],
        *[getattr(audoma_mixins, c) for c in dir(audoma_mixins) if c.endswith("Mixin")],
        *[
            getattr(audoma_serializers, c)
            for c in dir(audoma_serializers)
            if c.endswith("Serializer")
        ],
        *[
            getattr(audoma_generics, c)
            for c in dir(audoma_generics)
            if c.endswith("APIView")
        ],
    ]


def create_choices_enum_description(choices: Union[dict, List[Tuple]], field_name):

    if not isinstance(choices, dict):
        choices = dict(choices)

    description = f"Filter by {field_name} \n"
    for key, val in choices.items():
        description += f" * `{key}` - {val}\n"
    return description
