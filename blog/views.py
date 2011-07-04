# -*- encoding: utf-8 -*-
from django.db.models import Q
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.http import Http404
from blog.models import Post
from django.utils import translation
from taggit.models import Tag

def index(request, year=None, lang='sv'):
    translation.activate(lang)
    if year:
        head = u'inlägg från %s' % year
        posts = get_list_or_404(Post.objects.all().distinct() \
                                    .filter(update__time__year=year) \
                                    .order_by('update__time'))
        
        if not posts:
            raise Http404(u'Inga inlägg från %s.' % year)
    else:
        head = None
        posts = Post.objects.exclude(posted_time__exact=None) \
            .order_by('-update__time')[:5]
    
    return direct_to_template(request, 'blog/index.html', {
            'head': head,
            'lang': lang,
            'posts': posts,
            'years': [x.year for x
                      in Post.objects.dates('posted_time', 'year')],
            })

def post_detail(request, year, slug):
    post = get_object_or_404(Post, 
                             posted_time__year=year,
                             slug=slug)
    translation.activate(post.lang)
    
    return direct_to_template(request, 'blog/post_detail.html', {
            'post': post,
            'lang': post.lang,
            })

def tagcloud(request, lang='sv'):
    translation.activate(lang)
    return direct_to_template(request, 'blog/tagcloud.html')

def tagged(request, slug):
    tag = Tag.objects.get(slug=slug)
    posts = Post.objects.filter(tags__in=[tag])
    return direct_to_template(request, 'blog/tagged.html', {
            'tag': tag,
            'posts': posts,
            })
