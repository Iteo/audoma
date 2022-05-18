from django.contrib import admin

from .models import (
    ExampleFileModel,
    ExampleModel,
    ExamplePerson,
)


admin.site.register(ExamplePerson)
admin.site.register(ExampleModel)
admin.site.register(ExampleFileModel)
