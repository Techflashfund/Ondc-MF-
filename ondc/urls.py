from django.urls import path
from .views import ONDCSearchView

urlpatterns = [
    path("search/", ONDCSearchView.as_view()),
]
