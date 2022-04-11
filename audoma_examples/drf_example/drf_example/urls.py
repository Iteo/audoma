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
    ExampleViewSet,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import routers

from django.urls import re_path


router = routers.DefaultRouter()

# TODO FIX basenames
router.register(r"examples", ExampleViewSet, basename="examples")
router.register(r"model_examples", ExampleModelViewSet, basename="model-examples")
router.register(
    r"file-upload-example", ExampleFileUploadViewSet, basename="file-upload-example"
)
router.register(
    r"permissionless_model_examples",
    ExampleModelPermissionLessViewSet,
    basename="permissionless-model-examples",
)

urlpatterns = router.urls

urlpatterns += [
    re_path(r"^api/schema/$", SpectacularAPIView.as_view(), name="schema"),
    re_path(
        r"^swagger-ui/$",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    re_path(r"^redoc/$", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
