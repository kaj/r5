# -*- encoding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from blog.models import Post
from django.template import defaultfilters
from datetime import datetime
from django.utils import translation

def index(request, year=None, lang='sv'):
    translation.activate(lang)
    if year:
        all_posts = Post.objects.order_by('posted_time')
        head = u'inlägg från %s' % year
        posts = get_list_or_404(all_posts, posted_time__year=year)
    else:
        head = None
        posts = Post.objects.exclude(posted_time__exact=None)[:5]
    
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
