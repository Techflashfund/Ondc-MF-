from django.urls import path
from .views import *

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
    path('on_status',OnStatusView.as_view(),name='on_status'),
    path('on_update',OnUpdateView.as_view(),name='on_update'),
    path('digisend',DigiLockerFormSubmission.as_view(),name='digisend'),
    path('esignsub',EsignFormSubmission.as_view(),name='esignsub'),

    # Lumpsum
    path('lumpselect',Lumpsum.as_view(),name='lumpselect'),
    path('lumpformsub',LumpFormSub.as_view(), name='lumpformsub'),
    path('lumpinit',LumpINIT.as_view(),name='lumpinit'),
    path('lumpconfirm',ConfirmLump.as_view(),name='lumpconfirm'),
    
]

