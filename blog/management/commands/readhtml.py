from blog.models import Post, Update
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.redirects.models import Redirect
from xml.etree import ElementTree
import requests
import os

nsmap = {
    'db': 'http://docbook.org/ns/docbook',
    'r': 'http://www.kth.se/rasmusmarkup',
    'xl': 'http://www.w3.org/1999/xlink',
    'html': 'http://www.w3.org/1999/xhtml',
    }

class Command(BaseCommand):
    help = 'Find and read content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year', dest='year',
            help='Year (i.e. directory) of site to read')
        parser.add_argument(
            '--basedir', dest='base', default='dump',
            help='Base directory containing files to read (default: %(default)s)')
        parser.add_argument(
            '--make-images-public', dest='make_images_public', action='store_true',
            help='Tell rphotos that referensed images should be made public.')

    def handle(self, **options):
        base = options['base']
        self.make_images_public = options['make_images_public']
        if options['year']:
            base = os.path.join(base, options['year'])

        self.img_base = settings.IMG_BASE
        self.img_key = self.rphotos_login()

        for root, dirs, files in os.walk(base):
            #print "Current directory", root
            #print "Sub directories", dirs
            #print "Files", files
            for fn in files:
                if fn.endswith('.html') and not fn.startswith('.#'):
                    filename = os.path.join(root, fn)
                    try:
                        self.readfile(filename)
                    except Exception as err:
                        print("Failed to load %s" % filename)
                        raise

    def rphotos_login(self):
        response = requests.post(
            self.img_base + "/api/login",
            json = { 'user': settings.IMG_USER,
                     'password': settings.IMG_PASS },
        )
        response.raise_for_status()
        return response.json()['token']

    def readfile(self, filename):
        print("Handle %s" % filename)
        slug = os.path.basename(filename)[:-5]
        dirname = os.path.dirname(filename)
        #if slug in ['index', 'sv', 'en']:
        #    slug = os.path.basename(os.path.dirname(filename))
        if slug.endswith('.sv') or slug.endswith('.en'):
            slug = slug[:-3]
        else:
            print("Strange, language code missing in filename %s" % filename)

        for prefix, url in nsmap.items():
            ElementTree.register_namespace(prefix, url)

        tree = ElementTree.parse(filename)
        # Ok, I don't know if this is a good idea, but mark parents.
        # Maybe there is a flag to ElementTree that provides this instead?
        #for e in tree.iter():
        #    for child in list(e):
        #        child.parent = e

        date = self.parsedate(serialize(tree.find('head/pubdate', nsmap)))
        if not date:
            print("Ignoring %s, pubdate missing." % filename)
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
            rdate = self.parsedate(revision.get('date'))
            note = self.d2h(revision)
            # print rdate, note[:40]
            update, isnew = Update.objects.get_or_create(post=p, time=rdate)
            update.note = note
            update.save()

        p.posted_time = date
        p.title = self.d2h(tree.find('head/title', nsmap))
        p.abstract = self.d2h(tree.find('head/abstract', nsmap))
        p.content = self.d2h(tree.getroot(), dirname, str(date.year) if date else '')
        for image in tree.findall('.//figure'):
            if 'front' in image.get('class', ''):
                image.set('class', 'sidebar')
                p.frontimage = serialize(image, False)
        p.save()
        # print " ", date, slug, p.title, tags

    def d2h(self, elem, dirname='', year=''):
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
            if self.make_images_public:
                response = requests.post(
                    self.img_base + "/api/image/makepublic",
                    json = {'path': ref },
                    headers = { 'authorization': self.img_key }
                )
            else:
                response = requests.get(
                    self.img_base + "/api/image",
                    params = {'path': ref },
                    headers = { 'authorization': self.img_key }
                )
            response.raise_for_status()
            data = response.json()

            if not data.get('public', False):
                print("NOTE, image %s is not public" % ref)
            # TODO: Note if an image is "small" on server
            if 'scaled' in e.attrib.get('class', ''):
                medium = data['medium']
                img = ElementTree.Element('img', {
                    'src': self.img_base + medium['url'],
                    'alt': '',
                    'width': str(medium['width']),
                    'height': str(medium['height'])})
                e.insert(0, img)
            else:
                title = e.find('zoomcaption')
                a = ElementTree.Element('a', {
                    'href': self.img_base + data['medium']['url']
                })
                e.insert(0, a)
                if title is not None:
                    e.remove(title)
                    title = ElementTree.tostring(title, method='text', encoding='unicode')
                    a.set('title', title)
                small = data['small']
                img = ElementTree.SubElement(a, 'img', {
                    'src': self.img_base + small['url'],
                    'width': str(small['width']),
                    'height': str(small['height'])
                })
                if title:
                    img.set('alt', (u'Bild: %s') % a.get('title'))
                else:
                    caption = e.find('figcaption')
                    if caption is not None:
                        caption = ElementTree.tostring(caption, method='text', encoding='unicode')
                        img.set('alt', (u'Bild: %s') % caption)
                    else:
                        img.set('alt', (u'Bild'))

            del e.attrib['ref']

        return serialize(elem)

    def parsedate(self, datestr=None):
        if datestr:
            try:
                if len(datestr) < 20:
                    datestr = datestr + 'T12:00:00Z'
                return datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                print('WARNING: Failed to parse date "%s".' % datestr)
                return None
        else:
            return None

def serialize(elem, skip_root=True):
    if elem is None:
        return ''

    qnames, namespaces = ElementTree._namespaces(elem, None)

    if skip_root:
        elem.tag = None
    data = []
    ElementTree._serialize_xml(data.append, elem, qnames=qnames,
                               namespaces=namespaces, short_empty_elements=True)
    return "".join(data).strip()

def textcontent(e):
    if e is None:
        return ''

    return (e.text or '') + u''.join(textcontent(ee)+(ee.tail or '') for ee in list(e))

def redirect(old_path, new_path):
    if old_path == new_path:
        return
    redirect, _isnew = Redirect.objects.get_or_create(
        site_id=settings.SITE_ID,
        old_path=old_path)
    redirect.new_path = new_path
    redirect.save();
