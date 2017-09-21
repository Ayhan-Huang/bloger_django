"""Cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from app import views
from django.views.static import serve
from . import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),
    url(r'^index/', views.index, name='index'),
    url(r'^login/', views.my_login, name='login'),
    url(r'^logout/', views.my_logout, name='logout'),
    url(r'^register', views.register, name='register'),
    url(r'^type/(?P<article_type>\w+)', views.index),   # 首页类别路由
    url(r'changepassword', views.change_password, name='change_password'),
    url(r'^valid_code/', views.valid_code, name='valid_code'),
    url(r'^article_poll/', views.article_poll, name='article_poll'),
    url(r'^comment_poll/', views.comment_poll, name='comment_poll'),
    url(r'^write_comment/', views.write_comment, name='write_comment'),
    url(r'^follow/(?P<bloger>\w+)', views.follow),
    url(r'^upload/$', views.upload_file, name='upload_file'),
    # url(r'^accounts/login/$', 'django.contrib.auth.views.login',{'template_name': 'login.html'}),


    url(r'^blog/', include('app.urls')),  #路由分发

    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),  # 配置media路由
]
