from __future__ import absolute_import  # Python 2 only

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, ngettext
from jinja2 import evalcontextfilter, Markup, escape
from jinja2 import Environment
from jinja2 import nodes
from jinja2.ext import Extension
import re

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

class FragmentCacheExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['cache'])

    def __init__(self, environment):
        super(FragmentCacheExtension, self).__init__(environment)

        # add the defaults to the environment
        environment.extend(
            fragment_cache_prefix='',
            fragment_cache=None
        )

    def parse(self, parser):
        # the first token is the token that started the tag.  In our case
        # we only listen to ``'cache'`` so this will be a name token with
        # `cache` as value.  We get the line number so that we can give
        # that line number to the nodes we create by hand.
        lineno = parser.stream.next().lineno

        # now we parse a single expression that is used as cache key.
        args = [parser.parse_expression()]

        # if there is a comma, the user provided a timeout.  If not use
        # None as second parameter.
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))

        # now we parse the body of the cache block up to `endcache` and
        # drop the needle (which would always be `endcache` in that case)
        body = parser.parse_statements(['name:endcache'], drop_needle=True)

        # now return a `CallBlock` node that calls our _cache_support
        # helper method on this extension.
        return nodes.CallBlock(self.call_method('_cache_support', args),
                               [], [], body).set_lineno(lineno)

    def _cache_support(self, name, timeout, caller):
        """Helper callback."""
        key = self.environment.fragment_cache_prefix + name

        # try to load the block from the cache
        # if there is no fragment in the cache, render it and store
        # it in the cache.
        from django.core.cache import cache
        rv = cache.get(key)
        if rv is not None:
            return rv
        rv = caller()
        cache.set(key, rv, timeout)
        return rv


def maketagcloud(lang):
    from taggit.models import Tag
    from django.db.models import Count
    tags = Tag.objects.all().order_by('name').annotate(
        n = Count('taggit_taggeditem_items'))
    if tags:
        max_n = max(tag.n for tag in tags)
        exponent = 0.4
        c = 5.9 / pow(max_n, exponent)
        for tag in tags:
            tag.w = int(pow(tag.n, exponent)*c)
    return mark_safe(get_template('blog/part/tagcloud.html').render({'tags': tags}))

def makelatestcomments(lang):
    from r5comments.models import Comment
    comments = Comment.objects.filter(is_removed=False, is_public=True). \
               select_related('post'). \
               defer('post__abstract', 'post__content', 'post__frontimage'). \
               order_by('-submit_date')[:5]
    return mark_safe(get_template('blog/part/latestcomments.html').
                     render({'comments': comments}))

def render_books(books):
    template = get_template('books/part/book.html')
    def stars(r):
        if r:
            def t(name, n):
                return ('<span class="' + name + '"></span>') * n
            return mark_safe(t('star', int(r)) +
                             t('half', 0 if r.is_integer() else 1) +
                             t('no',   int(5-r)))
        else:
            return ''
    return '\n'.join(template.render({'book': b,
                                      'stars': stars(float(b.rating)/10)})
                     for b in books)

def environment(**options):
    from simplegravatar.templatetags.simplegravatar import show_gravatar_secure
    env = Environment(**options)
    def getlang():
        return translation.get_language() or 'sv'
    def langname(lang):
        return translation.get_language_info(lang).get('name_local')
    def tagcloud():
        from django.core.cache import cache
        lang = getlang()
        key = 'j_cloud_' + lang
        result = cache.get(key)
        if result is None:
            result = maketagcloud(lang)
            cache.set(key, result, , 30*60)
        return result
    def latestcomments():
        from django.core.cache import cache
        lang = getlang()
        key = 'j_latestcomments_' + lang
        result = cache.get(key)
        if result is None:
            result = makelatestcomments(lang)
            cache.set(key, result)
        return result
    def favbooks():
        from django.core.cache import cache
        lang = getlang()
        key = 'b_favbooks_' + lang
        result = cache.get(key)
        if result is None:
            from books.models import Book
            goodbooks = Book.objects.filter(rating__gte=40).order_by('?')[:4]
            result = render_books(goodbooks)
            cache.set(key, result, 30*60)
        return mark_safe(result)
    @evalcontextfilter
    def linebreaks(eval_ctx, value):
        result = u'\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
                            for p in _paragraph_re.split(escape(value)))
        if eval_ctx.autoescape:
            result = Markup(result)
        return result

    env.globals.update({
        'getlang': getlang,
        'langname': langname,
        'tagcloud': tagcloud,
        'latestcomments': latestcomments,
        'favbooks': favbooks,
        'gravatardata': show_gravatar_secure,
        'static': staticfiles_storage.url,
        'url': reverse,
    })
    env.filters['linebreaks'] = linebreaks
    env.install_gettext_callables(gettext, ngettext, newstyle=True)

    return env
