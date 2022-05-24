"""example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from audoma_api.views import (
    ExampleFileUploadViewSet,
    ExampleModelPermissionLessViewSet,
    ExampleModelViewSet,
    ExamplePersonModelViewSet,
    ExampleSimpleModelViewSet,
    ExampleViewSet,
    MutuallyExclusiveViewSet,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import routers

from django.contrib import admin
from django.urls import re_path

# special router to handle PATCH/PUT requests on list endpoints
from audoma.drf.routes import BulkRouter


bulk_router = BulkRouter()
router = routers.DefaultRouter()

bulk_router.register(r"bulk_endpoint", ExampleSimpleModelViewSet, "bulk-example")

router.register(r"examples", ExampleViewSet, basename="examples")
router.register(r"model_examples", ExampleModelViewSet, basename="model-examples")
router.register(
    r"model_person_example", ExamplePersonModelViewSet, basename="model-person-example"
)
router.register(
    r"file-upload-example", ExampleFileUploadViewSet, basename="file-upload-example"
)
router.register(
    r"mutually-exclusive", MutuallyExclusiveViewSet, basename="mutually-exclusive"
)
router.register(
    r"permissionless_model_examples",
    ExampleModelPermissionLessViewSet,
    basename="permissionless-model-examples",
)

urlpatterns = router.urls + bulk_router.urls

urlpatterns += [
    re_path("admin/", admin.site.urls),
    re_path(r"^api/schema/$", SpectacularAPIView.as_view(), name="schema"),
    re_path(
        r"^swagger-ui/$",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    re_path(r"^redoc/$", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
