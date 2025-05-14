from django.urls import path
from .views import ONDCSearchView,OnSearchView,OnSearchDataView,SIPCreationView,OnSelectSIPView,FormSubmisssion,INIT,ONINIT,ConfirmSIP,OnConfirmSIP

urlpatterns = [
    path("search/", ONDCSearchView.as_view()),
    path("on_search", OnSearchView.as_view(), name="on_search"),
    path("on_searchdata", OnSearchDataView.as_view(), name="on_search_data"),
    path('select/',SIPCreationView.as_view(),name='select'),
    path('on_select',OnSelectSIPView.as_view(),name='on_select'),
    path('formsub',FormSubmisssion.as_view(),name='formsub'),
    path('init/',INIT.as_view(),name='init'),
    path('on_init',ONINIT.as_view(),name='on_init'),
    path('confirm',ConfirmSIP.as_view(),name='confirm'),
    path('on_confirm',OnConfirmSIP.as_view(),name='on_confirm'),
]

