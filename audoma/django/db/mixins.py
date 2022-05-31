class ModelExampleMixin:
    def __init__(self, *args, **kwargs) -> None:
        if kwargs.get("example", None):
            self.example = kwargs.pop("example", None)
        super().__init__(*args, **kwargs)
