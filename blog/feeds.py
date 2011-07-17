# -*- encoding: utf-8 -*-
from django.contrib.syndication.views import Feed
from django.utils.safestring import mark_safe
from django.utils.feedgenerator import Atom1Feed
from django.shortcuts import get_object_or_404
from taggit.models import Tag
from blog.models import Post, Update
from views import filter_by_language

class UpdatesFeed(Feed):
    title = u'Rasmus.krats.se'
    subtitle = u'Uppdateringar på Rasmus.krats.se. Skriverier då och då, på webben sedan 1995.'
    link = '/'
    author_name = 'Rasmus Kaj'
    author_email = 'rasmus@krats.se'
    feed_type = Atom1Feed
    
    description_template = 'feed/description.html'

    def __init__(self, lang):
        self.lang = lang
        
    def items(self):
        updates = Update.objects.all().order_by('-time')[:10]
        return filter_by_language(updates, self.lang)[:5]

    def item_title(self, item):
        return mark_safe(item.post.title)

class TaggedUpdatesFeed(UpdatesFeed):

    def get_object(self, request, tag):
        return get_object_or_404(Tag, slug=tag)

    def title(self, obj):
        return u'Taggat %s på Rasmus.krats.se' % obj

    def items(self, obj):
        tagged = Post.objects.filter(tags__in=[obj])
        updates = Update.objects.filter(post__in=tagged).order_by('-time')[:10]
        return filter_by_language(updates, self.lang)[:5]
