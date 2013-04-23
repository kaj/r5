# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.comments.models import Comment
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseNotModified
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.utils import translation
from django.utils.http import http_date
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from django.views.static import was_modified_since
from logging import getLogger
from taggit.models import Tag
from time import mktime
from blog.models import Post, Update, Image
import os
import stat

logger = getLogger(__name__)

def index(request, year=None, lang=None):
    updates = Update.objects.all().select_related()
    if year:
        head = u'inlägg från %s' % year
        updates = get_list_or_404(updates \
                                      .filter(time__year=year) \
                                      .order_by('time'))
    else:
        head = None
        updates = updates.order_by('-time')[:10]

    if not lang:
        return redirect('index', year=year, lang=choose_lang(request))
    updates = filter_by_language(updates, lang)
    if not year:
        updates = updates[:5]
    translation.activate(lang)
    
    return direct_to_template(request, 'blog/index.html', {
            'year': year,
            'head': head,
            'lang': lang,
            'altlingos': langlinks('index', lang=lang, year=year),
            'updates': updates,
            'years': [x.year for x
                      in Post.objects.dates('posted_time', 'year')],
            })

def choose_lang(request, availiable=None):
    '''Choose the best language availiable based on the request meta.'''
    wanted = translation.trans_real.parse_accept_lang_header(
        request.META.get('HTTP_ACCEPT_LANGUAGE', ''))
    if availiable is None:
        availiable = {'sv', 'en'}
    for accept_lang, q in wanted:
        if accept_lang == '*':
            break;
        normalized = accept_lang.split('-', 1)[0]
        if normalized in availiable:
            return normalized
    # no match, fallback to "any" language
    return list(availiable)[0]

def post_detail(request, year, slug, lang=None):
    post_objects = Post.objects.filter(posted_time__year=year, slug=slug)
    try:
        post = get_object_or_404(post_objects, lang=lang)
        altlingos = post_objects \
            .exclude(lang=lang).values_list('lang', flat=True)
    except Http404:
        # Failed to get the requested language, try any other
        lingos = post_objects.values_list('lang', flat=True)
        if not lingos:
            raise Http404
        
        post = get_object_or_404(post_objects,
                                 lang=choose_lang(request, lingos))
        return redirect(post.get_absolute_url())
    
    similar = filter_by_language(post.tags.similar_objects(), post.lang,
                                 extra_skip=post)
    
    translation.activate(lang)
    message = None
    if 'c' in request.GET:
        comment = get_object_or_404(Comment, id=request.GET['c'])
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
            'altlingos': langlinks('post_detail', altlingos, 
                                   year=year, slug=slug),
            'similar': similar,
            'next': post.get_absolute_url(),
            })

def redirect_post(request, year, slug, lang=None):
    post_objects = Post.objects.filter(posted_time__year=year, slug=slug)
    try:
        post = get_object_or_404(post_objects, lang=lang)
    except Http404:
        lingos = post_objects.values_list('lang', flat=True)
        if not lingos:
            raise Http404
        
        post = get_object_or_404(post_objects,
                                 lang=choose_lang(request, lingos))
    return redirect(post.get_absolute_url())

def tagcloud(request, lang):
    if not lang:
        return redirect('tagcloud', lang=choose_lang(request))
    translation.activate(lang)
    return direct_to_template(request, 'blog/tagcloud.html', {
            'altlingos': langlinks('tagcloud', lang=lang),
            })

def tagged(request, slug, lang=None):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags__in=[tag])
    if not lang:
        lingos = get_list_or_404(posts.values_list('lang', flat=True))
        return redirect('tagged', slug=slug, lang=choose_lang(request, lingos))
    translation.activate(lang)
    posts = filter_by_language(posts, lang)
    return direct_to_template(request, 'blog/tagged.html', {
            'tag': tag,
            'posts': posts,
            'lang': lang,
            'altlingos': langlinks('tagged', lang=lang, slug=slug),
            })

def filter_by_language(posts, lang, extra_skip=None):
    def ref(p):
        return "%s/%s" % (p.year, p.slug)
    samelang = {ref(p) for p in posts if p.lang == lang}
    if extra_skip:
        samelang.add(ref(extra_skip))
    return [p for p in posts if p.lang == lang or ref(p) not in samelang]

def about(request, lang):
    translation.activate(lang)
    return direct_to_template(request, 'about.html', {
            'altlingos': langlinks('about', lang=lang),
            })

def langlinks(page, lingos=None, lang=None, **kwargs):
    if lingos is None:
        lingos = {'sv', 'en'} - {lang}
    return [ (l, reverse(page, kwargs=dict(lang=l, **kwargs)))
             for l in lingos
             ]

def image_small(request, slug):
    return image_view(request, slug, size=Image.ICON_MAX)

def image_view(request, slug, size=900):
    obj = get_object_or_404(Image, ref=slug)
    scaled_path = os.path.join(settings.SCALED_IMAGE_DIR,
                               '%s-%s' % (slug, size))
    try:
        return serve_file(request, path=scaled_path, mimetype=obj.mimetype)
    except Http404:
        from PIL import Image as PImage
        sourcedata = PImage.open(os.path.join(settings.IMAGE_FILES_BASE, obj.sourcename))
        scaleddata = sourcedata.resize(obj.scaled_size(size), int(PImage.ANTIALIAS))
        full_path = os.path.join(settings.MEDIA_ROOT, scaled_path)
        dir = os.path.dirname(full_path)
        if not os.path.exists(dir):
            os.makedirs(dir, 0777)
        scaleddata.save(full_path, sourcedata.format)
        return serve_file(request, path=scaled_path, mimetype=obj.mimetype)

def serve_file(request, path, mimetype):
    fullpath = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(fullpath):
        raise Http404(_(u'"%(path)s" does not exist') % {'path': fullpath})
    # Respect the If-Modified-Since header.
    statobj = os.stat(fullpath)
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj.st_mtime, statobj.st_size):
        return HttpResponseNotModified(mimetype=mimetype)
    with open(fullpath, 'rb') as f:
        response = HttpResponse(f.read(), mimetype=mimetype)
    response["Last-Modified"] = http_date(statobj.st_mtime)
    response["Expires"] = http_date_future(weeks=26)
    if stat.S_ISREG(statobj.st_mode):
        response["Content-Length"] = statobj.st_size
    return response
    
def http_date_future(**args):
    future=datetime.now() + timedelta(**args)
    return http_date(mktime(future.timetuple()))
