# -*- encoding: utf-8 -*-
from django.contrib.syndication.views import Feed
from django.utils.safestring import mark_safe
from django.utils.feedgenerator import Atom1Feed
from django.shortcuts import get_object_or_404
from taggit.models import Tag
from blog.models import Post, Update
from views import filter_by_language
from django.utils.translation import activate, ugettext_lazy as _

class UpdatesFeed(Feed):
    title = _(u'Rasmus.krats.se')
    subtitle = _(u'Uppdateringar på Rasmus.krats.se. Skriverier då och då, på webben sedan 1995.')
    link = '/'
    author_name = 'Rasmus Kaj'
    author_email = 'rasmus@krats.se'
    feed_type = Atom1Feed
    
    description_template = 'feed/description.html'

    def __init__(self, lang):
        self.lang = lang
        
    def __call__(self, request, *args, **kwargs):
        activate(self.lang)
        return super(UpdatesFeed, self).__call__(request, *args, **kwargs)
    
    def get_feed(self, obj, request):
        feed = super(UpdatesFeed, self).get_feed(obj, request)
        feed.feed['language'] = self.lang
        return feed

    def items(self):
        updates = Update.objects.all().order_by('-time')[:17]
        return filter_by_language(updates, self.lang)[:10]

    def item_title(self, item):
        return mark_safe(item.post.title)

    def item_pubdate(self, item):
        return item.time

class TaggedUpdatesFeed(UpdatesFeed):

    def get_object(self, request, tag):
        return get_object_or_404(Tag, slug=tag)

    def title(self, obj):
        return _(u'Taggat %s på Rasmus.krats.se') % obj

    def items(self, obj):
        tagged = Post.objects.filter(tags__in=[obj])
        updates = Update.objects.filter(post__in=tagged).order_by('-time')[:17]
        return filter_by_language(updates, self.lang)[:10]
