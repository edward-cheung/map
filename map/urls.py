"""map URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from topic import views

urlpatterns = [
                  path('admin/', admin.site.urls),
                  re_path(r'^$', views.index, name='index'),
                  re_path(r'^login/$', views.login, name='login'),
                  re_path(r'^register/$', views.register, name='register'),
                  re_path(r'^logout/$', views.logout, name='logout'),
                  re_path(r'^issue/$', views.issue, name='issue'),
                  re_path(r'^messages/$', views.messages, name='messages'),
                  re_path(r'^settings/$', views.settings, name='settings'),
                  re_path(r'^comment/$', views.comment, name='comment'),
                  re_path(r'^good/$', views.good, name='good')
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
