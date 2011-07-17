from django.conf.urls.defaults import patterns, url
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from blog.views import index, post_detail, tagcloud, tagged

def redirect_year(request, year):
    return redirect('/%s/' % year)

urlpatterns = patterns(
    '',
    url(r'^$', index, name='index'),
    url(r'^(?P<year>[0-9]{4})/$', index),
    url(r'^(?P<year>[0-9]{4})$', redirect_year),
    url(r'^(?P<year>[0-9]{4})/(?P<slug>[a-z0-9_-]+)$', post_detail),
    
    url(r'^tag/$', tagcloud),
    url(r'^tag/(?P<slug>[a-z0-9_]+)$', tagged),

    url(r'^robots\.txt$', direct_to_template, 
        {'template': 'robots.txt', 'mimetype': 'text/plain'}),
)
