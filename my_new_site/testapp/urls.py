from django.conf.urls import url

from . import views

import re

PAGE_RE = '(?P<pagename>/(?:[a-zA-Z0-9_-]+/?)*)'

urlpatterns = [
    #url(r'^/$', views.TestAppClass.as_view(), name='testappclass'),
    url(r'^/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^/signup/$', views.SignupView.as_view(), name='signup'),
    url(r'^/login/$', views.LoginView.as_view(), name='login'),
    url(r'^/logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^/welcome/$', views.WelcomeView.as_view(), name='welcome'),
    url(r'^/_history' + PAGE_RE, views.HistoryPageView.as_view(), name='historypage'),
    url(r'^/_edit' + PAGE_RE, views.EditPageView.as_view(), name='editpage'),    
    url(r'^' + PAGE_RE, views.WikiPageView.as_view(), name='wikipage'),
]  