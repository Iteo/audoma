from healthcare_api import views

from audoma.drf import routers


# from django.contrib import admin
# from django.urls import (
#     include,
#     re_path,
# )


router = routers.DefaultRouter()

router.register(r"patient", views.PatientViewset, basename="patient")
router.register(
    r"specialization", views.SpecializatioNViewSet, basename="specialization"
)
router.register(r"doctor", views.DoctorViewset, basename="doctor")


urlpatterns = [] + router.urls
