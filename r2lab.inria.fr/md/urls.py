from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url('^(?P<markdown_file>.+)$', views.show, name='show'),
    ]
