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

def select_texts(doc, selector):
    return [etree.tostring(e, method='text', encoding=unicode, with_tail=False)
            for e in CSSSelector(selector)(doc)]

class SimpleTest(TestCase):
    
    def setUp(self):
        self.c = Client()
        p, _ = Post.objects.get_or_create(
            title='Foo',
            posted_time= datetime(2013, 11, 5),
            lang = 'sv',
            abstract = '<p>Lorem ipsum dolor</p>\n',
            content='<p>En text som i princip.</p>\n' +
            '<p>Skulle kunna vara ganska intressant.</p>\n')
        Update.objects.get_or_create(post=p, time=p.posted_time)

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
        
    def test_base_url_redirects_to_lang(self):
        self.get('/', expected_status_code=302,
                 expected_location='/en')
    
    def test_get_frontpage(self):
        doc = self.get('/sv')
        
        self.assertEqual(['Rasmus.krats.se'],
                         select_texts(doc, 'head title'))
        self.assertEqual(['Rasmus.krats.se'],
                         select_texts(doc, 'header #sitename'))
        # TODO Have actual content in the test db and test for that.

    def test_get_nonexistant_page(self):
        doc = self.get('/2011/nonesuch', expected_status_code=404)
        
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

    def test_bad_c_is_404_not_5xx(self):
        doc = self.get('/2013/foo.sv?c=foo', expected_status_code=404)
