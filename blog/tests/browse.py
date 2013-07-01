"""
Test browsing public pages in the blog app.
"""

from django.test import TestCase
from django.test.client import Client
from lxml.cssselect import CSSSelector
import html5lib
from html5lib import treebuilders
from lxml import etree

def select_texts(doc, selector):
    return [etree.tostring(e, method='text', with_tail=False)
            for e in CSSSelector(selector)(doc)]

class SimpleTest(TestCase):
    
    def setUp(self):
        self.c = Client()
    
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
