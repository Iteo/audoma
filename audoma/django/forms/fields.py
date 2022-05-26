from decimal import Decimal

from django.forms import DecimalField


class MoneyField(DecimalField):
    def prepare_value(self, value) -> Decimal:
        return value.amount
