from django.conf.urls.defaults import patterns, url
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from blog.views import index, post_detail, tagcloud, tagged
from blog.feeds import UpdatesFeed, TaggedUpdatesFeed

def redirect_year(request, year):
    return redirect('/%s/' % year)

urlpatterns = patterns(
    '',
    url(r'^$', index, name='index'),
    url(r'^(?P<year>[0-9]{4})/$', index),
    url(r'^(?P<year>[0-9]{4})$', redirect_year),
    url(r'^(?P<year>[0-9]{4})/(?P<slug>[a-z0-9-]+)$', post_detail),
    
    url(r'^tag/$', tagcloud),
    url(r'^tag/(?P<slug>[a-z0-9-]+)$', tagged),

    url(r'^atom-en.xml$', UpdatesFeed('en')),
    url(r'^atom-sv.xml$', UpdatesFeed('sv')),
    url(r'^atom-en-(?P<tag>[a-z0-9-]+).xml$', TaggedUpdatesFeed('en')),
    url(r'^atom-sv-(?P<tag>[a-z0-9-]+).xml$', TaggedUpdatesFeed('sv')),

    url(r'^robots\.txt$', direct_to_template, 
        {'template': 'robots.txt', 'mimetype': 'text/plain'}),
)
