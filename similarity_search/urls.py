from django.urls import path
from .views import SimilaritySearchView

urlpatterns = [
    path('search/', SimilaritySearchView.as_view(), name='similarity-search'),
] 