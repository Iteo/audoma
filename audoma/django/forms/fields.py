from djmoney.forms.fields import MoneyField
from djmoney.settings import (
    CURRENCY_CHOICES,
    DECIMAL_PLACES,
)

from django.forms import (
    ChoiceField,
    DecimalField,
)

from audoma.django.forms.widgets import MoneyWidget


class MoneyField(MoneyField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
        )

        max_value = kwargs.pop("max_value", None)
        min_value = kwargs.pop("min_value", None)
        max_digits = kwargs.pop("max_digits", None)
        decimal_places = kwargs.pop("decimal_places", DECIMAL_PLACES)

        amount_field = DecimalField(
            *args,
            max_value=max_value,
            min_value=min_value,
            max_digits=max_digits,
            decimal_places=decimal_places,
        )

        self.widget = MoneyWidget(amount_widget=amount_field.widget)
