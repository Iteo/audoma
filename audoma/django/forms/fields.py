from django.forms import DecimalField


class MoneyField(DecimalField):
    def prepare_value(self, value):
        return value.amount
