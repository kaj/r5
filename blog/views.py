# -*- encoding: utf-8 -*-
from django.db.models import Q
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.http import Http404
from blog.models import Post, Update
from django.utils import translation
from taggit.models import Tag

def index(request, year=None):
    lang = _activatelang(request)
    
    updates = Update.objects.all().select_related()
    if year:
        head = u'inlägg från %s' % year
        updates = get_list_or_404(updates \
                                      .filter(time__year=year) \
                                      .order_by('time'))
        updates = filter_by_language(updates, lang)
    else:
        head = None
        updates = updates.order_by('-time')[:10]
        updates = filter_by_language(updates, lang)[:5]
    
    return direct_to_template(request, 'blog/index.html', {
            'head': head,
            'lang': lang,
            'updates': updates,
            'years': [x.year for x
                      in Post.objects.dates('posted_time', 'year')],
            })

def post_detail(request, year, slug):
    lang = _activatelang(request)
    try:
        post = get_object_or_404(Post, 
                                 posted_time__year=year,
                                 slug=slug,
                                 lang=lang)
    except:
        post = get_object_or_404(Post, 
                                 posted_time__year=year,
                                 slug=slug)

    similar = filter_by_language(post.tags.similar_objects(), post.lang,
                                 extra_skip=post.get_absolute_url())
    
    return direct_to_template(request, 'blog/post_detail.html', {
            'post': post,
            'lang': post.lang,
            'similar': similar,
            'next': post.get_absolute_url(),
            })

def tagcloud(request):
    _activatelang(request)
    return direct_to_template(request, 'blog/tagcloud.html')

def tagged(request, slug):
    lang = _activatelang(request)
    tag = Tag.objects.get(slug=slug)
    posts = filter_by_language(Post.objects.filter(tags__in=[tag]),
                               lang)
    return direct_to_template(request, 'blog/tagged.html', {
            'tag': tag,
            'posts': posts,
            })

def filter_by_language(posts, lang, extra_skip=None):
    samelang = set(p.get_absolute_url() for p in posts if p.lang == lang)
    if extra_skip:
        samelang.add(extra_skip)
    return [p for p in posts
            if p.lang == lang or p.get_absolute_url() not in samelang]

def about(request):
    _activatelang(request)
    return direct_to_template(request, 'about.html')

def _activatelang(request):
    lang = translation.get_language_from_request(request)
    translation.activate(lang)
    return lang
