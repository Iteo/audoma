from decimal import Decimal  # pragma: no cover

from django.forms import DecimalField  # pragma: no cover


class MoneyField(DecimalField):  # pragma: no cover
    def prepare_value(self, value) -> Decimal:
        return value.amount
