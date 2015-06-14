# -*- encoding: utf-8 -*-
"""
Test browsing public pages in the blog app.
"""

from django.test import TestCase
from django.test.client import Client
from lxml.cssselect import CSSSelector
import html5lib
from html5lib import treebuilders
from lxml import etree
from blog.models import Post, Update
from datetime import datetime
from re import sub
from r5comments.models import Comment

def select_texts(doc, selector):
    return [sub('\s+', ' ',
                etree.tostring(e, method='text', encoding=unicode, 
                               with_tail=False))
            for e in CSSSelector(selector)(doc)]

class BlogTestCase(TestCase):
    
    def setUp(self):
        self.c = Client()
        p, _ = Post.objects.get_or_create(
            title='Foo',
            posted_time= datetime(2013, 11, 5,  13, 47),
            lang = 'sv',
            abstract = '<p>Lorem ipsum dolor</p>\n',
            content='<p>En text som i princip.</p>\n' +
            '<p>Skulle kunna vara ganska intressant.</p>\n')
        Update.objects.get_or_create(post=p, time=p.posted_time)
        p.tags.add('junk', 'test')
    def get(self, url, expected_status_code=200, expected_location=''):
        response = self.c.get(url)
        self.assertEqual((expected_status_code, expected_location, 
                          'text/html; charset=utf-8'),
                         (response.status_code,
                          response.get('Location', '') \
                              .replace('http://testserver', ''),
                          response['Content-Type']))
    
        # NOTE Settings strict=False disables (all?) validation.
        # However, setting it to True gives bogus errors.
        parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("lxml"),
                                     strict=True, namespaceHTMLElements=False)
        
        try:
            if response.content:
                return parser.parse(response.content)
            else:
                return None

        except Exception:
            # NOTE Even though parser.errors is an array, it contains only first error.
            self.fail("Response is NOT valid HTML5: %s" %
                      ["%s, element: %s, pos: %s" % (error, element.get('name'), pos)
                       for pos, error, element in parser.errors])

class SimpleTest(BlogTestCase):
    def test_base_url_redirects_to_lang(self):
        self.get('/', expected_status_code=302,
                 expected_location='/en')
    
    def test_get_frontpage(self):
        doc = self.get('/sv')
        
        self.assertEqual(['Rasmus.krats.se'],
                         select_texts(doc, 'head title'))
        self.assertEqual(['Rasmus.krats.se'],
                         select_texts(doc, 'header #sitename'))
        self.assertEqual(['Foo'],
                         select_texts(doc, 'article h1'))
        self.assertEqual([u'Publicerad 2013-11-05 13:47 taggat junk, test.',
                          u'Lorem ipsum dolor',
                          u'Läs och kommentera inlägget Foo'],
                         select_texts(doc, 'article p'))

    def test_get_nonexistant_page(self):
        doc = self.get('/2011/nonesuch', expected_status_code=404)

    def test_get_existing_year(self):
        doc = self.get('/2013/sv')
        self.assertEqual(['Foo'],
                         select_texts(doc, 'article h1'))

    def test_get_nonexistant_year(self):
        doc = self.get('/1971/', expected_status_code=404)

    def test_tagcloud_redirects_to_lang(self):
        self.get('/tag/', expected_status_code=302,
                 expected_location='/tag/en')
    
    def test_get_tagcloud(self):
        doc = self.get('/tag/sv')
        
        self.assertEqual(['Rasmus.krats.se taggmoln'],
                         select_texts(doc, 'head title'))
        self.assertEqual(['Rasmus.krats.se'],
                         select_texts(doc, 'header #sitename'))
        self.assertEqual(['Taggmoln'],
                         select_texts(doc, 'main h1'))
        # TODO Have actual content in the test db and test for that.

    def test_get_nonexistant_tag(self):
        doc = self.get('/tag/nonesuch', expected_status_code=404)
        
    def test_get_article(self):
        doc = self.get('/2013/foo.sv')
        self.assertEqual([u'Foo \u2013 Rasmus.krats.se'],
                         select_texts(doc, 'head title'))
        self.assertEqual(['Rasmus.krats.se'],
                         select_texts(doc, 'header #sitename'))
        self.assertEqual(['Foo'],
                         select_texts(doc, 'main header h1'))

    def test_bad_c_is_404_not_5xx(self):
        doc = self.get('/2013/foo.sv?c=foo', expected_status_code=404)

class CommentedTest(BlogTestCase):
    def setUp(self):
        self.c = Client()
        p1, _ = Post.objects.get_or_create(
            title = 'Foo', lang = 'sv',
            posted_time = datetime(2013, 11, 5,  13, 47),
            abstract = '<p>Lorem ipsum dolor</p>\n',
            content='<p>En text som i princip.</p>\n' +
            '<p>Skulle kunna vara ganska intressant.</p>\n')
        Update.objects.get_or_create(post=p1, time=p1.posted_time)
        Comment.objects.get_or_create(
            post=p1, by_name='X', by_email='a@b', comment='Hejsan',
            submit_date=datetime(2013, 11, 6, 11, 12),
            is_public=True)
        p1.tags.add('junk', 'test')
        p2, _ = Post.objects.get_or_create(
            title = 'Bar', lang = 'sv',
            posted_time = datetime(2015, 6, 14,  18, 32),
            content='<p>En kort text.</p>\n')
        Update.objects.get_or_create(post=p2, time=p2.posted_time)
        p2.tags.add('test')
        Comment.objects.get_or_create(
            post=p2, by_name='X', by_email='a@b', comment='Hejsan',
            submit_date=datetime(2015, 6, 14, 18, 36),
            is_public=True)
        Comment.objects.get_or_create(
            post=p2, by_name='Y', by_email='a@b', comment='Hejsan',
            submit_date=datetime(2015, 6, 14, 18, 17),
            is_public=True)
        Comment.objects.get_or_create(
            post=p2, by_name='Z', by_email='a@z', comment='Spam',
            submit_date=datetime(2015, 6, 14, 18, 18),
            is_removed=True)
        Comment.objects.get_or_create(
            post=p2, by_name='Z', by_email='a@z', comment='Spam',
            submit_date=datetime(2015, 6, 14, 18, 18))
        p3, _ = Post.objects.get_or_create(
            title = 'Baz', lang = 'sv',
            posted_time = datetime(2015, 6, 14,  18, 34),
            content='<p>En till kort text.</p>\n')
        Update.objects.get_or_create(post=p3, time=p3.posted_time)
        p3.tags.add('test')

    def test_get_frontpage(self):
        doc = self.get('/sv')

        self.assertEqual(['Rasmus.krats.se'],
                         select_texts(doc, 'head title'))
        self.assertEqual(['Rasmus.krats.se'],
                         select_texts(doc, 'header #sitename'))
        self.assertEqual(['Baz', 'Bar', 'Foo'],
                         select_texts(doc, 'article h1'))
        self.assertEqual([u'Kommentera inlägget',
                          u'Läs 2 kommentarer',
                          u'Läs inlägget Foo och en kommentar'],
                         select_texts(doc, 'article p.readmore'))
