# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.comments.models import Comment
from django.http import Http404, HttpResponse
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
    except Http404:
        # Failed to get the requested language, try any other
        lingos = Post.objects.filter(posted_time__year=year, slug=slug) \
            .values_list('lang', flat=True)
        if not lingos:
            raise Http404
        
        post = get_object_or_404(Post, 
                                 posted_time__year=year,
                                 slug=slug,
                                 lang=lingos[0])
        altlingos = lingos[1:]
    similar = filter_by_language(post.tags.similar_objects(), post.lang,
                                 extra_skip=post.get_absolute_url())
    
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
            'lang': lang,
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
