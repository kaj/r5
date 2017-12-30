# -*- encoding: utf-8 -*-
"""
Test browsing public pages in the blog app.
"""

from django.test import TestCase
from django.test.client import Client
from django.utils.text import slugify
from lxml.cssselect import CSSSelector
import html5lib
from html5lib import treebuilders
from lxml import etree
from blog.models import Post, Update
from datetime import datetime, time
from re import sub
from r5comments.models import Comment

def select_texts(doc, selector):
    return [sub('\s+', ' ',
                etree.tostring(e, method='text', encoding=str,
                               with_tail=False))
            for e in CSSSelector(selector)(doc)]

def createPost(title, content, lang='sv', abstract='', tags=None,
               posted_time=None):
    post, _ = Post.objects.get_or_create(
        title=title, slug=slugify(title), lang=lang, posted_time=posted_time,
        abstract=abstract, content=content)
    Update.objects.get_or_create(post=post, time=post.posted_time)
    if tags:
        post.tags.add(*tags)

    class PostWrapper:
        def __init__(self, post):
            self.post = post

        def addComment(self, by_name, by_email, comment, submit_date,
                       is_public=True, is_removed=False):
            c, _ = Comment.objects.get_or_create(
                post=self.post, by_name=by_name, by_email=by_email, comment=comment,
                is_public=is_public, is_removed=is_removed)
            if isinstance(submit_date, time):
                c.submit_date=datetime.combine(self.post.posted_time,
                                               submit_date)
            else:
                c.submit_date=submit_date
            c.is_public=is_public
            c.is_removed=is_removed
            c.save()

    return PostWrapper(post)

class BlogTestCase(TestCase):
    
    def setUp(self):
        self.c = Client()
        createPost(title='Foo',
                   posted_time= datetime(2013, 11, 5,  13, 47),
                   abstract = '<p>Lorem ipsum dolor</p>\n',
                   content='<p>En text som i princip.</p>\n' +
                   '<p>Skulle kunna vara ganska intressant.</p>\n',
                   tags=['junk', 'test'])

    def get(self, url, expected_status_code=200, expected_location=''):
        response = self.c.get(url)
        self.assertEqual((url, expected_status_code, expected_location,
                          'text/html; charset=utf-8'),
                         (url, response.status_code,
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
        p1 = createPost(title = 'Foo',
                        posted_time = datetime(2013, 11, 5,  13, 47),
                        abstract = '<p>Lorem ipsum dolor</p>\n',
                        content='<p>En text som i princip.</p>\n' +
                        '<p>Skulle kunna vara ganska intressant.</p>\n',
                        tags = ['junk', 'test'])
        p1.addComment('Nisse', 'nisse@se', comment='Hejsan',
                      submit_date=datetime(2013, 11, 6, 11, 12),
                      is_public=True)
        p2 = createPost(title = 'Bar',
                        posted_time = datetime(2015, 6, 14,  18, 32),
                        content='<p>En kort text.</p>\n',
                        tags=['test'])
        p2.addComment('Nisse', 'nisse@se', comment='Hejsan',
                      submit_date=time(18, 36), is_public=True)
        p2.addComment('Kalle', 'kalle@com', comment='Hejsan',
                      submit_date=time(18, 17), is_public=True)
        p2.addComment('Spammer', 'a@xx', comment='Spam',
                      submit_date=time(18, 18),
                      is_removed=True)
        p2.addComment('Porn', 'p@xx', comment='Spam',
                      submit_date=time(18, 18), is_public=False)
        p3 = createPost(title = 'Baz',
                        posted_time = datetime(2015, 6, 14,  18, 34),
                        abstract='<p>Blahonga.</p>',
                        content='<p>En till kort text.</p>\n',
                        tags=['test'])
        p3.addComment('Spammer', 'a@xx', comment='Spam',
                      submit_date=time(18, 38),
                      is_public=False, is_removed=True)

    def test_get_frontpage(self):
        doc = self.get('/sv')

        self.assertEqual(['Rasmus.krats.se'],
                         select_texts(doc, 'head title'))
        self.assertEqual(['Rasmus.krats.se'],
                         select_texts(doc, 'header #sitename'))
        self.assertEqual(['Baz', 'Bar', 'Foo'],
                         select_texts(doc, 'article h1'))
        self.assertEqual([u'Läs och kommentera inlägget Baz',
                          u'Läs 2 kommentarer',
                          u'Läs inlägget Foo och en kommentar'],
                         select_texts(doc, 'article p.readmore'))

    def test_get_baz(self):
        '''A post with no public comments.'''
        doc = self.get('/2015/baz.sv')
        self.assertEqual(['Baz', 'Skriv en kommentar'],
                         select_texts(doc, 'main h1'))

    def test_get_bar(self):
        '''A post with two public comments.'''
        doc = self.get('/2015/bar.sv')
        self.assertEqual(['Bar', 'Kommentarer',
                          'Kalle, 2015-06-14 18:17',
                          'Nisse, 2015-06-14 18:36',
                          'Skriv en kommentar'],
                         select_texts(doc, 'main h1'))

    def test_get_foo(self):
        '''A post with one public comments.'''
        doc = self.get('/2013/foo.sv')
        self.assertEqual(['Foo', 'Kommentarer',
                          'Nisse, 2013-11-06 11:12',
                          'Skriv en kommentar'],
                         select_texts(doc, 'main h1'))
