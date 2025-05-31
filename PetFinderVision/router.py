from rest_framework.routers import DefaultRouter
from user_register.api import UserViewSet
from feedback.api import FeedbackViewSet
from advertisements.api import AdvertisementViewSet
from news.api import NewsViewSet
from marks.api import MarksViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("feedback", FeedbackViewSet, basename="feedback")
router.register("advertisements", AdvertisementViewSet, basename="advertisements")
router.register("news", NewsViewSet, basename="news")
router.register("marks", MarksViewSet, basename="marks")
