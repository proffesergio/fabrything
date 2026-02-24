from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VendorApplicationViewSet,
    VendorProfileViewSet,
    VendorStatsViewSet,
    ApplicationStatusViewSet
)

router = DefaultRouter()
router.register(r'applications', VendorApplicationViewSet, basename='vendor-applications')
router.register(r'profile', VendorProfileViewSet, basename='vendor-profile')
router.register(r'stats', VendorStatsViewSet, basename='vendor-stats')
router.register(r'my-application', ApplicationStatusViewSet, basename='vendor-my-application')

urlpatterns = [
    path('', include(router.urls)),
]
