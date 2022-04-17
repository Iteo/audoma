from drf_spectacular.drainage import set_override

from audoma.examples import (
    DEFAULT,
    Example,
    NumericExample,
    RegexExample,
)


class ExampleMixin:
    audoma_example_class = Example

    def __init__(self, *args, example=DEFAULT, **kwargs):
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
    audoma_example_class = NumericExample


class RegexExampleMixin(ExampleMixin):
    audoma_example_class = RegexExample
