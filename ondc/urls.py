from django.urls import path
from .views import ONDCSearchView,OnSearchView,OnSearchDataView

urlpatterns = [
    path("search/", ONDCSearchView.as_view()),
    path("on_search", OnSearchView.as_view(), name="on_search"),
    path("on_searchdata", OnSearchDataView.as_view(), name="on_search_data"),
]
