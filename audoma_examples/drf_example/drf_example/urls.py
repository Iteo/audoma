from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from django.contrib import admin
from django.urls import (
    include,
    re_path,
)


urlpatterns = (
    re_path("v1/", include("drf_example.v1_urls")),
    re_path("v2/", include("drf_example.v2_urls")),
    re_path("admin/", admin.site.urls),
    re_path(r"^schema/$", SpectacularAPIView.as_view(), name="schema"),
    re_path(
        r"^swagger-ui/$",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    re_path(r"^redoc/$", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
)
