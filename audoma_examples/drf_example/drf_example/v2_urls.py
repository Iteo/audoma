from healthcare_api import views

from audoma.drf import routers


# from django.contrib import admin
# from django.urls import (
#     include,
#     re_path,
# )


router = routers.DefaultRouter()

router.register(r"patient", views.PatientViewset, basename="patient")


urlpatterns = [] + router.urls
