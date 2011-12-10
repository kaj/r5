# -*- encoding: utf-8 -*-
from django.contrib.comments.models import Comment
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from taggit.models import Tag
from blog.models import Post, Update

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
        altlingos = Post.objects.filter(posted_time__year=year, slug=slug) \
            .exclude(lang=lang).values_list('lang', flat=True)
    except:
        post = get_object_or_404(Post, 
                                 posted_time__year=year,
                                 slug=slug)
        altlingos = []
    similar = filter_by_language(post.tags.similar_objects(), post.lang,
                                 extra_skip=post.get_absolute_url())
    
    message = None
    if 'c' in request.GET:
        comment = Comment.objects.get(id=request.GET['c'])
        print "Comment:", comment
        if comment.is_removed:
            print "That comment is removed!!"
            message = _(u'Din kommentar är borttagen.')
        elif not comment.is_public:
            print "That comment awaits moderation!!"
            message = _(u'Din kommentar väntar på moderering.')
        else:
            return redirect('%s#c%d' % (post.get_absolute_url(), comment.id))
        
    return direct_to_template(request, 'blog/post_detail.html', {
            'post': post,
            'message': message,
            'lang': post.lang,
            'altlingos': altlingos,
            'similar': similar,
            'next': post.get_absolute_url(),
            })

def tagcloud(request):
    _activatelang(request)
    return direct_to_template(request, 'blog/tagcloud.html')

def tagged(request, slug):
    lang = _activatelang(request)
    tag = get_object_or_404(Tag, slug=slug)
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
    lang = request.GET.get('l')
    if lang:
        request.session['django_language'] = lang
    else:
        lang = translation.get_language_from_request(request)
    translation.activate(lang)
    return lang
