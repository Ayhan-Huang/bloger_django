from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<sitename>\w+)/$', views.home),
    url(r'^(?P<sitename>\w+)/articles/(?P<condition>category|tag|date)/(?P<title>.+)/', views.home),
    url(r'^(?P<sitename>\w+)/p/(?P<article_id>\d+)/', views.article),
    url(r'^(?P<sitename>\w+)/write_article/$', views.write_article, name='write_article'),
    url(r'^(?P<sitename>\w+)/management/$', views.management, name='management'),
    url(r'^(?P<sitename>\w+)/management/del/$', views.delete_article, name='delete_article'),
    url(r'^(?P<sitename>\w+)/management/edit/(?P<article_id>\d+)/$', views.edit_article, name='edit_article'),
    url(r'^$', views.index),
]

