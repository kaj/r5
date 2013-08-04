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
        make_option('--year', help='Year (i.e. directory) of site to read',
                    dest='year'),
        )
    
    def handle_noargs(self, **options):
        base = 'dump'
        
        if options['year']:
            base = os.path.join(base, options['year'])
        
        for root, dirs, files in os.walk(base):
            #print "Current directory", root
            #print "Sub directories", dirs
            #print "Files", files
            for fn in files:
                if fn.endswith('.html') and not fn.startswith('.#'):
                    filename = os.path.join(root, fn)
                    try:
                        readfile(filename)
                    except Exception as err:
                        print "Failed to load %s" % filename
                        raise err

def readfile(filename):
    print "Handle", filename
    slug = os.path.basename(filename)[:-5]
    dirname = os.path.dirname(filename)
    #if slug in ['index', 'sv', 'en']:
    #    slug = os.path.basename(os.path.dirname(filename))
    if slug.endswith('.sv') or slug.endswith('.en'):
        slug = slug[:-3]
    else:
        print "Strange, language code missing in filename %s" % filename
    
    for prefix, url in nsmap.items():
        ElementTree.register_namespace(prefix, url)

    tree = ElementTree.parse(filename)
    # Ok, I don't know if this is a good idea, but mark parents.
    # Maybe there is a flag to ElementTree that provides this instead?
    for e in tree.iter():
        for child in list(e):
            child.parent = e
    
    date = parsedate(serialize(tree.find('head/pubdate', nsmap)))
    if not date:
        print "Print ignoring %s, pubdate missing." % filename
        return
    
    lang = tree.getroot().get('lang')
    p, isnew = Post.objects.get_or_create(posted_time__year=date.year,
                                          slug=slug,
                                          lang=lang,
                                          defaults={'posted_time': date})

    tags = [textcontent(e) for e in (tree.getroot().findall('head/tag', nsmap) or [])]
    if tags:
        p.tags.add(*tags)
    
    # Create an empty update for original posting
    Update.objects.filter(post=p).delete()
    update, isnew = Update.objects.get_or_create(post=p, note='',
                                                 defaults={'time': date})
    if not isnew:
        update.time=date
        update.save()
    for revision in tree.findall('./head/update', nsmap):
        rdate = parsedate(revision.get('date'))
        note = d2h(revision)
        # print rdate, note[:40]
        update, isnew = Update.objects.get_or_create(post=p, time=rdate)
        update.note = note
        update.save()
    
    p.posted_time = date
    p.title = d2h(tree.find('head/title', nsmap))
    p.abstract = d2h(tree.find('head/abstract', nsmap))
    p.content = d2h(tree.getroot(), dirname, str(date.year) if date else '')
    for image in tree.findall('.//figure'):
        if 'front' in image.get('class', ''):
            del image.attrib['class']
            p.frontimage = serialize(image, False)
    p.save()
    # print " ", date, slug, p.title, tags

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

    info = elem.find('./head', nsmap)
    if info is not None:
        info.clear()
        info.tag = None

    for e in elem.iter():
        link = e.get('href')
        if link:
            # TODO Figure out a good way to hande media files.
            pass
    
    for e in elem.findall('.//figure', nsmap):
        ref = e.get('ref')
        try:
            e.set('ref', Image.objects.get(sourcename=ref).ref)
        except Exception as err:
            # TODO Check for file and create new Image object!
            raise RuntimeError("WARNING: image data missing: %s" % ref)
    
    return serialize(elem)

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
