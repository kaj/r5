from django import template
from django.contrib.comments.models import Comment
from taggit.models import Tag
from math import pow

register = template.Library()

@register.inclusion_tag('blog/publine.html')
def publine(post):
    return {
        'time': post.posted_time,
        'tags': post.tags.all(),
        }

@register.inclusion_tag('blog/part_tagcloud.html')
def tagcloud():
    tags = Tag.objects.all().order_by('name')
    if tags:
        for tag in tags:
            tag.n = tag.taggit_taggeditem_items.count()
        max_n = max(tag.n for tag in tags)
        exponent = 0.4
        c = 5.9 / pow(max_n, exponent)
        for tag in tags:
            tag.w = int(pow(tag.n, exponent)*c)
    return {
        'tags': tags,
        }

@register.inclusion_tag('blog/part_latestcomments.html')
def latestcomments():
    return {
        'comments': Comment.objects.filter(is_public=True) \
            .order_by('-submit_date')[:5],
        }

@register.inclusion_tag('blog/post_summary.html')
def updatesummary(update):
    return {
        'update': update,
        'post': update.post,
        }

@register.inclusion_tag('blog/post_summary.html')
def postsummary(post):
    return {
        'post': post,
        'update': None,
        }
