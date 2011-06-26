from django.conf.urls.defaults import patterns, url
from blog.views import index, post_detail

urlpatterns = patterns(
    '',
    url(r'^$', index, name='index'),
    url(r'^(?P<year>[0-9]{4})/$', index),
    url(r'^(?P<year>[0-9]{4})/(?P<slug>[a-z0-9_-]+)$', post_detail),
)
