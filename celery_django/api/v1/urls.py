from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import ClientViewSet, MailingViewSet, InfoViewSet


router = DefaultRouter()
router.register("clients", ClientViewSet, basename="clients")
router.register("mailings/info", InfoViewSet, basename="info")
router.register("mailings", MailingViewSet, basename="mailings")

urlpatterns = [
    path("", include(router.urls)),
]
