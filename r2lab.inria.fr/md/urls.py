from django.conf.urls import url

from . import views

urlpatterns = [
    url('^(?P<markdown_file>.*)$', views.markdown_page, name='show'),
    ]
