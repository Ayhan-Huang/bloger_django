from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<sitename>\w+)/$', views.home, name='home'),
    url(r'^(?P<sitename>\w+)/articles/(?P<condition>category|tag|date)/(?P<title>.+)/', views.home, name='home'),
    url(r'^(?P<sitename>\w+)/p/(?P<article_id>\d+)/$', views.article, name='article'),
    url(r'^$', views.index),
]

