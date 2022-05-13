from django.contrib import admin

from .models import (
    Account,
    Auction,
)


admin.site.register(Account)
admin.site.register(Auction)
