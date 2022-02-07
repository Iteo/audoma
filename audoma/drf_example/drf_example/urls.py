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
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api.views import ExampleViewSet
from api.views import ExampleModelViewSet
from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

router = routers.DefaultRouter()

router.register(r'examples', ExampleViewSet, basename='examples')
router.register(r'model_examples', ExampleModelViewSet, basename='model-examples')

urlpatterns = router.urls

schema_view = get_schema_view(
    openapi.Info(
        title="audoma API",
        default_version='2.1',
        description="short description",
        validators=['ssv'],
        # terms_of_service="https://www.google.com/policies/terms/",
        # contact=openapi.Contact(email="contact@snippets.local"),
        # license=openapi.License(name="Proprietary")
    ),
    patterns=urlpatterns,
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
  re_path(r'^docs/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
