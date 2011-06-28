from blog.models import Post
from datetime import datetime
from django.conf import settings
from django.core.management.base import NoArgsCommand
from xml.etree import ElementTree
import os

nsmap = {
    'db': 'http://docbook.org/ns/docbook',
    'r': 'http://www.kth.se/rasmusmarkup',
    'xl': 'http://www.w3.org/1999/xlink',
    }

def parsedate(datestr=None):
    if datestr:
        try:
            if len(datestr) < 20:
                datestr = datestr + 'T12:00:00Z'
            return datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            print 'WARNING: Failed to parse date "%s".' % datestr
            return None
    else:
        return None

class Command(NoArgsCommand):
    help = 'Find and read content'
    
    def handle_noargs(self, **options):
        base = settings.CONTENT_FILES_BASE
        
        for root, dirs, files in os.walk(base):
            #print "Current directory", root
            #print "Sub directories", dirs
            #print "Files", files
            for fn in files:
                if fn.endswith('.docb'):
                    filename = os.path.join(root, fn)
                    try:
                        readfile(filename)
                    except:
                        print "Failed to load %s" % filename
                        raise

def readfile(filename):
    print "Handle", filename
    slug = os.path.basename(filename)[:-5]
    dirname = os.path.dirname(filename)
    if slug in ['index', 'sv', 'en']:
        t = os.path.basename(os.path.dirname(filename))
        if slug == 'index':
            slug = t
        else:
            slug = t + '.' + slug
    if slug.endswith('.sv'):
        slug = slug[:-3] + '_sv'
    if slug.endswith('.en'):
        slug = slug[:-3] + '_en'

    for prefix, url in nsmap.items():
        ElementTree.register_namespace(prefix, url)

    tree = ElementTree.parse(filename)

    date = parsedate(serialize(tree.find('db:info/db:pubdate', nsmap)))
    p, isnew = Post.objects.get_or_create(posted_time=date, slug=slug)

    p.title = d2h(tree.find('db:info/db:title', nsmap))
    p.abstract = d2h(tree.find('db:info/db:abstract', nsmap))
    p.content = d2h(tree.getroot(), dirname)
    p.save()
    print " ", date, slug, p.title

def d2h(elem, dirname=''):
    if elem is None:
        return ''

    info = elem.find('db:info', nsmap)
    if info is not None:
        info.clear()
        info.tag = None

    for docb, html in (('db:para', 'p'), 
                       ('db:phrase', 'span'), ('db:acronym', 'abbr'),
                       ('db:emphasis', 'em'),
                       ('db:itemizedlist', 'ul'), ('db:listitem', 'li'),
                       ('db:table', 'table'), ('db:thead', 'thead'),
                       ('db:summary', 'summary'),
                       ('db:tr', 'tr'), ('db:th', 'th'), ('db:td', 'td'),
                       ('db:sidebar', 'aside'),
                       ('db:quote', 'q')):
        for e in elem.findall('.//' + docb, nsmap):
            # print "Found element", e, "changing to", html
            e.tag = html

    # Inline simple stuff, put it in a span with the docbook name as class
    for docb in ('personname', 'orgname', 'filename', 'tag'):
        for e in elem.findall('.//db:' + docb, nsmap):
            e.tag = 'span'
            e.set('class', (e.get('class', '') + ' ' + docb).strip())
    
    for e in elem.iter():
        link = e.get('{http://www.w3.org/1999/xlink}href')
        if link:
            makelink(e, link)
            del e.attrib['{http://www.w3.org/1999/xlink}href']
        role = e.get('role')
        if role == 'wp':
            lang = 'sv' # TODO current language
            makelink(e, u'http://%s.wikipedia.org/wiki/%s' % (lang, e.text))
        elif role == 'sw':
            makelink(e, u'http://seriewikin.serieframjandet.se/index.php/%s' % e.text)

    for e in elem.findall('.//r:image', nsmap):
        e.tag = 'span'
        e.set('class', 'image ' + e.get('class', ''))
        imgref = e.get('ref')
        aimg, aicon = getimginfo(dirname)
        img = aimg.get(imgref)
        icon = aicon.get(imgref)
        if icon and img:
            a = ElementTree.SubElement(e, 'a', dict(href=img['name']))
            ElementTree.SubElement(
                a, 'img', dict(src=icon['name'],
                               width=icon['width'], height=icon['height']))
            title = e.find('db:title', nsmap)
            if title is not None:
                a.set('title', title.text)
                e.remove(title)
        else:
            print "WARNING: image data missing:", imgref

    return serialize(elem)

def makelink(e, href):
    """Convert the element e to a link to href."""
    if e.tag == 'span':
        # Simply replace this element with a link
        e.tag = 'a'
        e.set('href', href)
    else:
        content = list(e)
        a = ElementTree.SubElement(e, 'a', {'href': href})
        for ee in content:
            e.remove(ee)
            a.append(ee)
        a.text = e.text
        e.text = None

def getimginfo(dirname):
    img = {}
    icon = {}
    t = ElementTree.parse(dirname + '/imginfo.xml')
    for i in t.findall('.//img'):
        fullname = i.get('id')
        name, _dot, suffix = fullname.rpartition('.')
        if name.endswith('.i'):
            ref = name[:-2]
            icon[ref] = dict(name=fullname,
                             width=i.get('width'), height=i.get('height'))
        else:
            img[name] = dict(name=fullname,
                             width=i.get('width'), height=i.get('height'))
    return img, icon

def serialize(elem):
    if elem is None:
        return ''

    qnames, namespaces = ElementTree._namespaces(
        elem, 'utf8', None
        )

    elem.tag = None
    data = []
    ElementTree._serialize_xml(data.append, elem, encoding='utf8',
                               qnames=qnames, namespaces=namespaces)
    return "".join(data).decode('utf8').strip()
