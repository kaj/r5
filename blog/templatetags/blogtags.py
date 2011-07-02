from django import template

register = template.Library()

@register.inclusion_tag('blog/publine.html')
def publine(post):
    return {
        'time': post.posted_time,
        'tags': post.tags.all(),
        }
