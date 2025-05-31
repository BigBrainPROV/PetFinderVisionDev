from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import AdvertisementViewSet, analyze_photo_standalone

router = DefaultRouter()
router.register(r'advertisements', AdvertisementViewSet, basename='advertisement')

urlpatterns = [
    path('', include(router.urls)),
    path('analyze-photo/', analyze_photo_standalone, name='analyze_photo_standalone'),
] 