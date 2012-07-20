from blog.models import Post, Update, Image
from datetime import datetime
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.contrib.redirects.models import Redirect
from xml.etree import ElementTree
from shutil import copy
from urllib import quote
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
    
    date = parsedate(serialize(tree.find('db:info/db:pubdate', nsmap)))
    if not date:
        print "Print ignoring %s, pubdate missing." % filename
        return
    
    lang = tree.getroot().get('{http://www.w3.org/XML/1998/namespace}lang')
    p, isnew = Post.objects.get_or_create(posted_time__year=date.year,
                                          slug=slug,
                                          lang=lang,
                                          defaults={'posted_time': date})

    tags = [textcontent(e) for e in (tree.getroot().findall('.//db:subject', nsmap) or [])]
    if tags:
        p.tags.add(*tags)
    
    # Create an empty update for original posting
    update, isnew = Update.objects.get_or_create(post=p, time=date)
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
        if 'front' in image.get('class'):
            del image.attrib['class']
            p.frontimage = serialize(image, False)
    p.save()
    # print " ", date, slug, p.title, tags

    op = filename[len(settings.CONTENT_FILES_BASE)-1:-5]
    redirect(op, p.get_absolute_url())
    redirect(op + '.html', p.get_absolute_url())
    if any(op.endswith(t) for t in ['index', 'sv', 'en']):
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
            attrib.tag = 'p'
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
        p.set('class', 'formalpara')
        e.remove(title)
        p.insert(0, title)
        title.tail = title.tail + p.text
        p.text = None
    
    for e in elem.findall('.//r:java', nsmap):
        # width and height attribs are kept.
        jclass = e.get('class')
        del e.attrib['class']
        jar = e.get('jar')
        del e.attrib['jar']
        e.tag = 'object'
        e.set('codetype', 'application/java')
        e.set('classid', 'java:%s.class' % jclass)
        e.set('archive', jar)
        for p in e.findall('r:param', nsmap):
            p.tag = 'param'
    
    # Inline simple stuff, put it in a span with the docbook name as class
    for docb in ('personname', 'orgname', 'filename', 'tag', 'replaceable', 'remark'):
        for e in elem.findall('.//db:' + docb, nsmap):
            e.tag = 'span'
            e.set('class', (e.get('class', '') + ' ' + docb).strip())

    for mymark in ('book',):
        for e in elem.findall('.//r:' + mymark, nsmap):
            e.tag = 'span'
            e.set('class', (e.get('class', '') + ' ' + mymark).strip())
    
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
            # TODO: Handle my "local protocols", lj:, rfc:
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
                
        role = e.get('role')
        if role == 'wp':
            lang = getLanguage(e)
            ref = quote(textcontent(e).encode('utf8'))
            makelink(e, u'http://%s.wikipedia.org/wiki/%s' % (lang, ref))
        elif role == 'sw':
            ref = quote(textcontent(e).encode('utf8'))
            makelink(e, u'http://seriewikin.serieframjandet.se/index.php/%s' % ref)

    imginfo = None
    for e in elem.findall('.//r:image', nsmap):
        e.tag = 'figure'
        e.set('class', 'image ' + e.get('class', ''))
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
    langattr = "{http://www.w3.org/XML/1998/namespace}lang"
    if langattr in e.keys():
        return e.get(langattr)
    else:
        return getLanguage(e.parent)
    
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
