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
    AccountViewSet,
    AnonymousAccountViewSet,
    AuctionViewSet,
    CarViewSet,
    ExampleSimpleModelViewSet,
    ExampleViewSet,
    ManufacturerViewSet,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import routers

from django.contrib import admin
from django.urls import re_path

from audoma.drf.routes import BulkRouter


bulk_router = BulkRouter()
router = routers.DefaultRouter()

bulk_router.register(r"bulk_endpoint", ExampleSimpleModelViewSet, "bulk-example")
router.register(r"examples", ExampleViewSet, basename="examples")
router.register(r"accounts", AccountViewSet, basename="accounts_viewset")
router.register(r"auctions", AuctionViewSet, basename="auctions_viewset")
router.register(
    r"anonymous_accounts",
    AnonymousAccountViewSet,
    basename="anonymous_accounts_viewset",
)
router.register(
    r"manufacturer_viewset",
    ManufacturerViewSet,
    basename="manufacturer_viewset",
)
router.register(
    r"car_viewset",
    CarViewSet,
    basename="car_viewset",
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
