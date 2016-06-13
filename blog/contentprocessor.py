from books.models import Book, BookTag
from django.utils.safestring import mark_safe
from logging import getLogger
from lxml.etree import fromstring, Element, SubElement, tostring
from os.path import commonprefix
from re import match, findall
from taggit.models import Tag
from urllib.parse import quote
from .util import render_books
from django.utils.translation import ugettext as _

logger = getLogger(__name__)

def process_content(content, images, base=None, lang='sv'):
    dom = fromstring(u'<article lang="%s">%s</article>' % (lang, content))
    def getlang(elem):
        return elem.get('lang') or getlang(elem.getparent())
    for books in dom.iterfind('.//books'):
        tag = BookTag.objects.get(slug=books.attrib['tag'])
        result = render_books([to.content_object
                               for to in tag.books_taggedbook_items.all()])
        # Workaround for broken parser:
        result = result.replace('</span>', ' </span>')
        bp = books.getparent()
        npre = fromstring('<div class="ltbooks">'+result+'</div>')
        bp.insert(bp.index(books), npre)
        bp.remove(books)

    for figure in dom.iterfind('.//figure'):
        ref = figure.attrib['ref']
        del figure.attrib['ref']
        try:
            info = images.get(ref=ref)
        except:
            figure.text = ' (image not found) '
            logger.warning('Image %s not found' % ref)
            continue

        if info.is_small or 'scaled' in figure.attrib.get('class', ''):
            img = Element('img', {'src': info.large,
                                  'alt': '',
                                  'width': str(info.width),
                                  'height': str(info.height)})
            figure.insert(0, img)
        else:
            title = figure.xpath('zoomcaption')
            a = Element('a', {'href': info.large})
            figure.insert(0, a)
            if len(title) == 1:
                a.set('title', tostring(title[0], method='text',
                                        encoding=str, with_tail=False))
                figure.remove(*title)
            img = SubElement(a, 'img', {'src': info.icon,
                                        'width': str(info.iwidth),
                                        'height': str(info.iheight)})
            if len(title) == 1:
                img.set('alt', _(u'Bild: %s') % a.get('title'))
            else:
                caption = figure.xpath('figcaption')
                if len(caption) == 1:
                    img.set('alt', _(u'Bild: %s') % tostring(caption[0],
                                                            method='text',
                                                            encoding=str,
                                                            with_tail=False))
                else:
                    img.set('alt', _(u'Bild'))

    for e in dom.iterfind('.//a'):
        href = e.attrib.get('href', '')
        if href.startswith('rfc:'):
            e.set('href', 'http://tools.ietf.org/html/rfc' + href[4:])
        elif href.startswith('lj:'):
            e.set('href', 'http://' + href[3:] + '.livejournal.com/')
        elif base and not match('^([a-z]+:|/)', href):
            e.set('href', base + href)

    for e in dom.iterfind('.//term'):
        href = e.get('href', '')
        if not href:
            urlbase = {
                'wp': 'http://{lang}.wikipedia.org/wiki/{ref}',
                'sw': 'http://seriewikin.serieframjandet.se/index.php/{ref}',
                'foldoc': 'http://foldoc.org/{ref}',
            }
            ref = e.text
            disambiguion = e.get('da')
            if disambiguion:
                ref = ref + ' (' + disambiguion + ')'
                del e.attrib['da']
            e.set('href', urlbase.get(e.get('role') or 'wp', '').format(
                lang=getlang(e),
                ref=quote(ref)))
        e.tag = 'a'
    
    for e in dom.iterfind('.//uri'):
        e.tag = 'a'
        href = e.text
        e.set('href', href if ':' in href else 'http://' + href)

    for e in dom.iterfind('.//email'):
        e.tag = 'a'
        e.set('class', 'email')
        e.set('href', 'mailto:' +  e.text)

    for e in dom.iterfind('.//cite'):
        isbn = e.get('isbn')
        if isbn:
            # TODO Maybe put the link inside or around the cite?
            e.tag = 'a'
            e.set('href', 'http://{lang}.librarything.com/isbn/{isbn}'.format(
                lang = getlang(e),
                isbn=isbn))
        elif e.text:
            m = match('^Fa\s+([\d]+)(-\d+)?\s+([\d]+)$', e.text)
            if m:
                e.tag = 'a'
                e.set('href', 'https://fantomenindex.krats.se/{year}#i{i}'.format(
                    year = m.group(3),
                    i = m.group(1)))

    for pre in dom.iterfind('.//pre'):
        if len(pre):
            next
        content = tostring(pre, method='text', encoding=str,
                           with_tail=False).rstrip()
        indent = commonprefix(findall('\n *(?!\s)', content))
        if indent:
            content = content.replace(indent, '\n')

        cls = {c for c in pre.attrib.get('class', '').split()}
        if 'programlisting' in cls and len(cls) == 2:
            try:
                lang, = cls - {'programlisting'}
                from pygments import highlight
                from pygments.lexers import get_lexer_by_name
                from pygments.formatters import HtmlFormatter

                lexer = get_lexer_by_name(lang)
                formatter = HtmlFormatter(nowrap=True)
                result = highlight(content, lexer, formatter)
                pp = pre.getparent()
                npre = fromstring('<pre>'+result+'</pre>')
                npre.attrib.update(pre.attrib)
                pp.insert(pp.index(pre), npre)
                pp.remove(pre)
            except Exception as e:
                print("Error handling pre", cls, ":", e)
        else:
            pre.text = content
    return mark_safe((dom.text or u'') +
                     u''.join(tostring(x, encoding=str)
                              for x in dom.iterchildren()))
