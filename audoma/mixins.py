from drf_spectacular.drainage import set_override

# TODO - import examples, this will be better idea
from audoma.examples import (
    DEFAULT,
    Base64Example,
    DateExample,
    DateTimeExample,
    Example,
    NumericExample,
    RangeExample,
    RegexExample,
    TimeExample,
)


class ExampleMixin:
    """
    A mixin class that adds an example to the field in documentation by overriding
    `field` parameter in `_spectacular_annotation`.

    Args:
        audoma_example_class : Type[Example]
            The class that will be used to create the example.
            Depends on the type of field
    """

    audoma_example_class = Example

    def __init__(self, *args, example=DEFAULT, **kwargs) -> None:
        self.audoma_example = self.audoma_example_class(self, example)
        super().__init__(*args, **kwargs)
        example = self.audoma_example.get_value()
        if example is not DEFAULT:
            has_annotation = (
                hasattr(self, "_spectacular_annotation")
                and "field" in self._spectacular_annotation
                and isinstance(self._spectacular_annotation["field"], dict)
            )
            example_representation = self.audoma_example.to_representation(example)
            field = {"example": example_representation}
            if has_annotation:
                field = self._spectacular_annotation["field"].copy()
                field["example"] = example_representation

            set_override(
                self,
                "field",
                field,
            )


class NumericExampleMixin(ExampleMixin):
    """
    A mixin class that adds an example to the field in documentation for numeric fields
    """

    audoma_example_class = NumericExample


class RegexExampleMixin(ExampleMixin):
    """
    A mixin class that adds an example to the field in documentation for regex fields
    """

    audoma_example_class = RegexExample


class Base64ExampleMixin(ExampleMixin):
    audoma_example_class = Base64Example


class DateExampleMixin(ExampleMixin):
    audoma_example_class = DateExample


class TimeExampleMixin(ExampleMixin):
    audoma_example_class = TimeExample


class DateTimeExampleMixin(ExampleMixin):
    audoma_example_class = DateTimeExample


class RangeExampleMixin(ExampleMixin):
    audoma_example_class = RangeExample


class ModelExampleMixin:
    def __init__(self, *args, **kwargs) -> None:
        if kwargs.get("example", None):
            self.example = kwargs.pop("example", None)
        super().__init__(*args, **kwargs)
