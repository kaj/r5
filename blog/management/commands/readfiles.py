from blog.models import Post, Update, Image
from datetime import datetime
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.contrib.redirects.models import Redirect
from optparse import make_option
from shutil import copy
from urllib import quote
from xml.etree import ElementTree
import os

nsmap = {
    'db': 'http://docbook.org/ns/docbook',
    'r': 'http://www.kth.se/rasmusmarkup',
    'xl': 'http://www.w3.org/1999/xlink',
    'html': 'http://www.w3.org/1999/xhtml',
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

    option_list = NoArgsCommand.option_list + (
        make_option('--part', help='Part (i.e. year) of site to read',
                    dest='part'),
        )
    
    def handle_noargs(self, **options):
        base = settings.CONTENT_FILES_BASE
        
        if options['part']:
            base = os.path.join(base, options['part'])
        
        for root, dirs, files in os.walk(base):
            #print "Current directory", root
            #print "Sub directories", dirs
            #print "Files", files
            for fn in files:
                if fn.endswith('.docb') and not fn.startswith('.#'):
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
        slug = os.path.basename(os.path.dirname(filename))
    if slug.endswith('.sv') or slug.endswith('.en'):
        slug = slug[:-3]

    for prefix, url in nsmap.items():
        ElementTree.register_namespace(prefix, url)

    tree = ElementTree.parse(filename)
    # Ok, I don't know if this is a good idea, but mark parets.
    # Maybe there is a flag to ElementTree that provides this instead?
    for e in tree.iter():
        for child in list(e):
            child.parent = e
        
        xxns = '{http://www.w3.org/XML/1998/namespace}'
        for xattr in ('lang', 'id'):
            if e.get(xxns + xattr):
                e.set(xattr, e.get(xxns + xattr))
                del e.attrib[xxns + xattr]
    
    date = parsedate(serialize(tree.find('db:info/db:pubdate', nsmap)))
    if not date:
        print "Print ignoring %s, pubdate missing." % filename
        return
    
    lang = tree.getroot().get('lang')
    p, isnew = Post.objects.get_or_create(posted_time__year=date.year,
                                          slug=slug,
                                          lang=lang,
                                          defaults={'posted_time': date})

    tags = [textcontent(e) for e in (tree.getroot().findall('.//db:subject', nsmap) or [])]
    if tags:
        p.tags.add(*tags)
    
    # Create an empty update for original posting
    Update.objects.filter(post=p).delete()
    update, isnew = Update.objects.get_or_create(post=p, note='',
                                                 defaults={'time': date})
    if not isnew:
        update.time=date
        update.save()
    for revision in tree.findall('db:info//db:revision', nsmap):
        rdate = parsedate(serialize(revision.find('db:date', nsmap)))
        note = d2h(revision.find('db:revremark', nsmap)) or \
            d2h(revision.find('db:revdescription', nsmap))
        # print rdate, note[:40]
        update, isnew = Update.objects.get_or_create(post=p, time=rdate)
        update.note = note
        update.save()
    
    p.posted_time = date
    p.title = d2h(tree.find('db:info/db:title', nsmap))
    p.abstract = d2h(tree.find('db:info/db:abstract', nsmap))
    p.content = d2h(tree.getroot(), dirname, str(date.year) if date else '')
    for image in tree.findall('.//figure'):
        if 'front' in image.get('class', ''):
            del image.attrib['class']
            p.frontimage = serialize(image, False)
    p.save()
    # print " ", date, slug, p.title, tags

    op = filename[len(settings.CONTENT_FILES_BASE)-1:-5]
    if op[:6] != '/%d/' % p.posted_time.year:
        redirect(op, p.get_absolute_url())
        redirect(op + '.html', p.get_absolute_url())
    if any(op.endswith(t) for t in ['/index', '/sv', '/en']):
        redirect(os.path.dirname(op) + '/', p.get_absolute_url())

def redirect(old_path, new_path):
    if old_path == new_path:
        return
    redirect, _isnew = Redirect.objects.get_or_create(
        site_id=settings.SITE_ID,
        old_path=old_path)
    redirect.new_path = new_path
    redirect.save();

def d2h(elem, dirname='', year=''):
    if elem is None:
        return ''

    info = elem.find('db:info', nsmap)
    if info is not None:
        info.clear()
        info.tag = None

    for docb, html in (('db:para', 'p'), 
                       ('db:phrase', 'span'),
                       ('db:citetitle', 'cite'),
                       ('db:acronym', 'abbr'), ('db:abbrev', 'abbr'),
                       ('db:emphasis', 'em'), ('db:code', 'code'),
                       ('db:literallayout', 'pre'),
                       ('db:varlistentry/db:term', 'dt'),
                       ('db:varlistentry/db:listitem', 'dd'),
                       ('db:varlistentry', None),
                       ('db:variablelist', 'dl'),
                       ('db:orderedlist', 'ol'),
                       ('db:itemizedlist', 'ul'), ('db:listitem', 'li'),
                       ('db:simplelist', 'ul'), ('db:member', 'li'),
                       ('db:table', 'table'),
                       ('db:thead', 'thead'), ('db:tbody', 'tbody'),
                       ('db:summary', 'summary'), ('db:caption', 'caption'),
                       ('db:tr', 'tr'), ('db:th', 'th'), ('db:td', 'td'),
                       ('db:sidebar', 'aside'),
                       ('db:subscript', 'sub'), ('db:superscript', 'sup'),
                       ('db:quote', 'q'),
                       ('db:note', 'div'),
                       ('db:uri', 'uri'), ('db:email', 'email'),
                       ('html:script', 'script'),
                       ('r:br', 'br')):
        for e in elem.findall('.//' + docb, nsmap):
            # print "Found element", e, "changing to", html
            e.tag = html

    for e in elem.findall('.//db:section', nsmap):
        e.tag = 'section';
        t = e.find('db:title', nsmap)
        if t is not None:
            t.tag = 'h1'

    for e in elem.findall('.//db:info', nsmap):
        e.tag = 'section';
        e.set('class', 'info')
        t = e.find('db:title', nsmap)
        if t is not None:
            t.tag = 'h1'

    for e in elem.findall('.//db:blockquote', nsmap):
        e.tag = 'blockquote'
        attrib = e.find('db:attribution', nsmap)
        if attrib is not None:
            attrib.tag = 'footer'
            attrib.set('class', 'attribution')
            e.remove(attrib)
            e.append(attrib)
    
    for e in elem.findall('.//db:programlisting', nsmap):
        e.tag = 'pre'
        language = e.get('language')
        if language:
            e.set('class', 'programlisting ' + language)
            del e.attrib['language']
        else:
            e.set('class', 'programlisting')
        
    for e in elem.findall('.//db:formalpara', nsmap):
        e.tag = None
        title = e.find('db:title', nsmap)
        title.tag = 'strong'
        p = e.find('p')
        e.remove(title)
        p.insert(0, title)
        title.tail = u' \u2013 ' + title.tail + p.text
        p.text = None
    
    for e in elem.findall('.//r:java', nsmap):
        e.tag = 'object'
        # width and height attribs are kept.
        e.set('type', 'application/x-java-applet')
        for name, val in (('code', e.get('class')), ('archive', e.get('jar'))):
            pe = ElementTree.Element('param', {'name':name, 'value':val})
            pe.tail = e.text # The correct indent (should be ws only).
            e.insert(0, pe)
        del e.attrib['class']
        del e.attrib['jar']
        
        for p in e.findall('r:param', nsmap):
            p.tag = 'param'
    
    for e in elem.findall('.//db:tag', nsmap):
        e.tag = 'code'
        if e.get('class') in ('numcharref', 'paramentity'):
            e.text = '&' + e.text + ';';
        elif e.get('class') == 'attribute':
            pass
        elif not e.get('class'):
            e.text = '<' + e.text + '>';
        else:
            raise RuntimeError('Unsupported <tag class="%s">' % e.get('class'))
        e.set('class', 'xml')
    
    # Inline simple stuff, put it in a span with the docbook name as class
    for docb, html in (('personname', 'span'), ('orgname', 'span'), 
                       ('filename', 'span'), ('replaceable', 'em'),
                       ('remark', 'span')):
        for e in elem.findall('.//db:' + docb, nsmap):
            e.tag = html
            e.set('class', (e.get('class', '') + ' ' + docb).strip())

    for e in elem.findall('.//r:book', nsmap):
        e.tag = 'cite'
        e.set('class', (e.get('class', '') + ' ' + 'book').strip())
    
    for docb in ('command', ):
        for e in elem.findall('.//db:' + docb, nsmap):
            e.tag = 'code'
            e.set('class', (e.get('class', '') + ' ' + docb).strip())
    
    for e in elem.iter():
        title = e.get('{http://www.w3.org/1999/xlink}title')
        if title:
            del e.attrib['{http://www.w3.org/1999/xlink}title']
            e.set('title', title)
        
        link = e.get('{http://www.w3.org/1999/xlink}href')
        if link:
            makelink(e, link)
            del e.attrib['{http://www.w3.org/1999/xlink}href']
            if ((not any(link.startswith(t) for t in
                         ['#', 'http:', 'https:', 'mailto:', 'ftp:', 'lj:', 'rfc:', 'todo:', '../bm/'])) and
                (not any(link.endswith(t) for t in
                         ['/', '.html', '.en', '.sv', 'atom-sv.xml', 'atom-en.xml']))):
                # print "I think %s is a media file in %s for %s." % (link, dirname, year)
                todir = os.path.join(settings.MEDIA_ROOT, year)
                if not os.path.exists(todir):
                    # print "Creating dir", todir
                    os.makedirs(todir)
                try:
                    copy(os.path.join(dirname, link), todir)
                    redirect(os.path.join('/', dirname[len(settings.CONTENT_FILES_BASE):], link),
                             os.path.join('/', year, link))
                except:
                    print "WARNING: Failed to copy media %s in %s to %s." % (link, dirname, year)

        if e.tag in ('term', 'a'):
            next
                
        role = e.get('role')
        if role in ['wp', 'sw', 'foldoc']:
            makelink(e, tag='term')

    imginfo = None
    for e in elem.findall('.//r:image', nsmap):
        e.tag = 'figure'
        if e.get('class'):
            e.set('class', e.get('class'))
        imgref = e.get('ref')
        
        if not imginfo:
            imginfo = ImageFinder(dirname)
        img = imginfo.getimage(imgref)
        icon = imginfo.geticon(imgref)
        altelem = e.find('r:alt', nsmap)
        alt = textcontent(altelem)
        if altelem is not None:
            e.remove(altelem)

        # TODO Unify title and para in a good way?
        for alt in e.findall('r:alt', nsmap):
            alt.tag = 'alt'
        
        for title in e.findall('db:title', nsmap):
            title.tag = 'zoomcaption'
        for para in e.findall('p', nsmap): # mapped earlier!
            para.tag = 'figcaption'
        
        if not img:
            raise RuntimeError("WARNING: image data missing: %s" % imgref)
    
    if imginfo:
        imginfo.handleUsed(year)

    return serialize(elem)

def getLanguage(e):
    langattr = "lang"
    if langattr in e.keys():
        return e.get(langattr)
    else:
        return getLanguage(e.parent)
    
def makelink(e, href=None, tag='a'):
    """Convert the element e to a link to href."""
    if e.get('role') == 'wp':
        # Wikipedia is default place to lookup terms, so dont point it here.
        del e.attrib['role']
    if e.tag in ('span', 'term'):
        # Simply replace this element with a link
        e.tag = tag
        if href:
            e.set('href', href)
    else:
        content = list(e)
        a = ElementTree.SubElement(e, tag)
        if href:
            a.set('href', href)
        for ee in content:
            e.remove(ee)
            a.append(ee)
        if e.get('role'):
            a.set('role', e.get('role'))
            del e.attrib['role']
        a.text = e.text
        e.text = None

class ImageFinder:
    
    def __init__(self, dirname):
        self.dirname = dirname
        self.subdir = dirname[len(settings.CONTENT_FILES_BASE):]
        self.img = {}
        self.icon = {}
        self.used = []
        t = ElementTree.parse(dirname + '/imginfo.xml')
        for i in t.findall('.//img'):
            fullname = i.get('id')
            name, _dot, suffix = fullname.rpartition('.')
            if name.endswith('.i') or name.endswith('-i'):
                ref = name[:-2]
                self.icon[ref] = dict(name=fullname,
                                      width=i.get('width'),
                                      height=i.get('height'))
            else:
                self.img[name] = dict(name=fullname,
                                      sourcename=i.get('src'),
                                      width=i.get('width'),
                                      height=i.get('height'))
    
    def getimage(self, name):
        result = self.img.get(name)
        if result:
            Image.objects.get_or_create(
                sourcename=result['sourcename'],
                defaults={'ref': name,
                          'orig_width': result['width'],
                          'orig_height': result['height']})
            self.used.append(result['name'])
        return result
    
    def geticon(self, name):
        result = self.icon.get(name)
        if result:
            self.used.append(result['name'])
        return result

    def handleUsed(self, year):
        if True:
            return
        path = self.dirname[len(settings.CONTENT_FILES_BASE):]
        # print "Image files in %s: %s" % (path, self.used)
        todir = os.path.join(settings.MEDIA_ROOT, year)
        if not os.path.exists(todir):
            # print "Creating dir", todir
            os.makedirs(todir)
        for filename in self.used:
            src = os.path.join(self.dirname, filename)
            dst = os.path.join(todir, filename)
            if not os.path.exists(dst):
                # print "Copy %s to %s" % (src, dst)
                copy(src, dst)
            else:
                print "Target %s allready there." % dst
            srcurl = os.path.join('/', path, filename)
            dsturl = '/%s/%s' % (year, filename)
            redirect(srcurl, dsturl)
            srcurl, _dot, _suffix = srcurl.rpartition('.')
            redirect(srcurl, dsturl)

def serialize(elem, skip_root=True):
    if elem is None:
        return ''

    qnames, namespaces = ElementTree._namespaces(
        elem, 'utf8', None
        )

    if skip_root:
        elem.tag = None
    data = []
    ElementTree._serialize_xml(data.append, elem, encoding='utf8',
                               qnames=qnames, namespaces=namespaces)
    return "".join(data).decode('utf8').strip()

def textcontent(e):
    if e is None:
        return ''
    
    return (e.text or '') + u''.join(textcontent(ee)+(ee.tail or '') for ee in list(e))
