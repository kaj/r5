from django.conf.urls.defaults import patterns, url
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from blog.views import index, post_detail, tagcloud, tagged, about, image_small, image_view
from blog.feeds import UpdatesFeed, TaggedUpdatesFeed

def redirect_year(request, year):
    return redirect('/%s/' % year)

urlpatterns = patterns(
    '',
    url(r'^(?P<lang>(sv|en)?)$', index, {'year': None}, name='index'),
    url(r'^(?P<year>[0-9]{4})/(?P<lang>(sv|en)?)$', index, name='index'),
    url(r'^(?P<year>[0-9]{4})$', redirect_year), 
    url(r'^(?P<year>[0-9]{4})/(?P<slug>[a-z0-9-]+)\.(?P<lang>(sv|en))$',
        post_detail, name='post_detail'),
    url(r'^(?P<year>[0-9]{4})/(?P<slug>[a-z0-9-]+)/?$', post_detail),
    url(r'^img/(?P<slug>[a-z0-9_-]+)\.i', image_small, name='image_small'),
    url(r'^img/(?P<slug>[a-z0-9_-]+)', image_view, name='image_view'),
    
    url(r'^tag/(?P<lang>(sv|en)?)$', tagcloud, name='tagcloud'),
    url(r'^tag/(?P<slug>[a-z0-9-]+)$', tagged, name='tagged'),
    url(r'^tag/(?P<slug>[a-z0-9-]+)\.(?P<lang>(sv|en))$', tagged, name='tagged'),

    url(r'^about$', about, {'lang': 'en'}, name='about'),
    url(r'^om$', about, {'lang': 'sv'}, name='about'),

    url(r'^atom-en.xml$', UpdatesFeed('en'), name='atom-en'),
    url(r'^atom-sv.xml$', UpdatesFeed('sv'), name='atom-sv'),
    url(r'^atom-en-(?P<tag>[a-z0-9-]+).xml$', TaggedUpdatesFeed('en'),
        name='atom-tag-en'),
    url(r'^atom-sv-(?P<tag>[a-z0-9-]+).xml$', TaggedUpdatesFeed('sv'),
        name='atom-tag-sv'),

    url(r'^robots\.txt$', direct_to_template, 
        {'template': 'robots.txt', 'mimetype': 'text/plain'}),
)
