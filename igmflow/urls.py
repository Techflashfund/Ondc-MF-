from django.urls import path
from .views import *

urlpatterns=[
    path('issue/',IGMIssue.as_view(),name='issue'),
    path('on_issue',OnIssueView.as_view(),name='on_issue'),
]