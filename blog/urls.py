from django.conf.urls import patterns, url as django_url
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from blog.views import index, post_detail, tagcloud, tagged, about, image_small, image_view, redirect_post
from blog.feeds import UpdatesFeed, TaggedUpdatesFeed
import re

def redirect_year(request, year):
    return redirect('/%s/' % year)

class UrlShortcut:
    def __init__(self):
        self.bound = {}
        self.default = r'[a-z0-9-]+'
        
    def bind(self, name, pattern):
        self.bound[name] = pattern
        
    def __call__(self, pattern, *args, **kwargs):
        def djangify(m):
            p = m.group(1)
            return r'(?P<%s>%s)' % (p, self.bound.get(p, self.default))
        return django_url(re.sub(r'<(\w+)>', djangify, pattern),
                          *args, **kwargs)

url = UrlShortcut()
url.bind('year', '[0-9]{4}')
url.bind('lang', '(sv|en)')
url.bind('imgid', '[a-z0-9_-]+')

urlpatterns = patterns(
    '',
    url(r'^<lang>?$', index, {'year': None}, name='index'),
    url(r'^<year>/<lang>?$', index, name='index'),
    url(r'^<year>$', redirect_year), 
    url(r'^<year>/<slug>\.<lang>$', post_detail, name='post_detail'),
    url(r'^<year>/<slug>/?$',       post_detail),
    url(r'^<year>/<slug>([/\.]<lang>)?(/|.html|)$', redirect_post),
    url(r'^img/<imgid>\.i', image_small, name='image_small'),
    url(r'^img/<imgid>', image_view, name='image_view'),
    
    url(r'^tag/<lang>?$', tagcloud, name='tagcloud'),
    url(r'^tag/<slug>$', tagged, name='tagged'),
    url(r'^tag/<slug>\.<lang>$', tagged, name='tagged'),

    url(r'^about$', about, {'lang': 'en'}, name='about'),
    url(r'^om$', about, {'lang': 'sv'}, name='about'),

    url(r'^atom-en.xml$', UpdatesFeed('en'), name='atom-en'),
    url(r'^atom-sv.xml$', UpdatesFeed('sv'), name='atom-sv'),
    url(r'^atom-en-<tag>.xml$', TaggedUpdatesFeed('en'),
        name='atom-tag-en'),
    url(r'^atom-sv-<tag>.xml$', TaggedUpdatesFeed('sv'),
        name='atom-tag-sv'),

    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt',
                                               content_type='text/plain')),
)
