# -*- encoding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from blog.models import Post
from django.template import defaultfilters
from datetime import datetime

def index(request, year=None):
    if year:
        all_posts = Post.objects.order_by('posted_time')
        head = u'inlägg från %s' % year
        posts = get_list_or_404(all_posts, posted_time__year=year)
    else:
        head = u'Rasmus.krats.se'
        posts = Post.objects.exclude(posted_time__exact=None)[:50]
    
    return direct_to_template(request, 'blog/index.html', {
            'head': head,
            'posts': posts,
            'years': [x.year for x
                      in Post.objects.dates('posted_time', 'year')],
            })

def post_detail(request, year, slug):
    post = get_object_or_404(Post, 
                             posted_time__year=year,
                             slug=slug)
    
    return direct_to_template(request, 'blog/post_detail.html', {
            'post': post,
            })
