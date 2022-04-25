from djmoney.forms import MoneyWidget
from djmoney.settings import CURRENCY_CHOICES

from django.forms import (
    MultiWidget,
    Select,
    TextInput,
)


class MoneyWidget(MultiWidget):
    def __init__(
        self,
        choices=CURRENCY_CHOICES,
        amount_widget=TextInput,
        currency_widget=None,
        default_currency=None,
        *args,
        **kwargs
    ):
        self.default_currency = default_currency
        if not currency_widget:
            currency_widget = Select(choices=choices)
        widgets = (amount_widget,)
        super().__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if value is not None:
            if isinstance(value, (list, tuple)):
                return value
            return [value.amount, value.currency]
        return [None, self.default_currency]
