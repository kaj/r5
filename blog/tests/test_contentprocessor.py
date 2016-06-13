"""
Test the blog module
"""

from django.test import TestCase
from blog.contentprocessor import *
from blog.models import Image

class imagecollection:
    def __init__(self, data):
        self.data = data
        
    def get(self, ref):
        return self.data[ref]

class ContentProcessorTest(TestCase):

    def setUp(self):
        self.images = imagecollection({
            'foo': Image(ref='foo', sourcename='dir/foo.jpg',
                         orig_width=848, orig_height=565,
                         mimetype='image/jpeg')
            })
        
        
    def test_process_simple_figure(self):
        INPUT = '\n'.join([
                '<figure class="image sidebar" ref="foo" />',
                '<p>Lorem ipsum.</p>'
                ])
        
        EXPECTED = '\n'.join([
                '<figure class="image sidebar"><a href="/img/foo"><img height="133" src="/img/foo.i" width="200" alt="Bild"/></a></figure>',
                '<p>Lorem ipsum.</p>'
                ])
        
        self.assertEqual(EXPECTED, process_content(INPUT, self.images))

    def test_process_figure_with_title(self):
        INPUT = ''.join([
                '<figure class="image sidebar" ref="foo">',
                '<zoomcaption>Foo</zoomcaption>',
                '</figure>',
                '<p>Lorem ipsum.</p>'
                ])
        
        EXPECTED = u''.join([
                '<figure class="image sidebar">',
                '<a href="/img/foo" title="Foo"><img height="133" src="/img/foo.i" width="200" alt="Bild: Foo"/></a>',
                '</figure>',
                '<p>Lorem ipsum.</p>'
                ])
        
        self.assertEqual(EXPECTED, process_content(INPUT, self.images))

    def test_process_nonexistant_figure(self):
        INPUT = '\n'.join([
                '<figure class="image sidebar" ref="nonesuch" />',
                '<p>Lorem ipsum.</p>'
                ])

        EXPECTED = '\n'.join([
                '<figure class="image sidebar"> (image not found) </figure>',
                '<p>Lorem ipsum.</p>'
                ]) 
        self.assertEqual(EXPECTED, process_content(INPUT, self.images))

    def test_process_figure_with_caption(self):
        INPUT = ''.join([
                '<figure class="image sidebar" ref="foo">',
                '<zoomcaption>Foo</zoomcaption>',
                '<figcaption>This is some kind of caption.</figcaption>',
                '</figure>',
                '<p>Lorem ipsum.</p>'
                ])
        
        EXPECTED = u''.join([
                '<figure class="image sidebar">',
                '<a href="/img/foo" title="Foo"><img height="133" src="/img/foo.i" width="200" alt="Bild: Foo"/></a>',
                '<figcaption>This is some kind of caption.</figcaption>',
                '</figure>',
                '<p>Lorem ipsum.</p>'
                ])
        
        self.assertEqual(EXPECTED, process_content(INPUT, self.images))

    def test_process_figure_with_caption(self):
        INPUT = '<term da="film">Åskbollen</term>'
        EXPECTED = '<a href="http://sv.wikipedia.org/wiki/%C3%85skbollen%20%28film%29">Åskbollen</a>'
        self.assertEqual(EXPECTED, process_content(INPUT, self.images))

#def t():
#    process_content_etree(INPUT)

# timeit.repeat(stmt=t, number=1000)
# [0.05785393714904785, 0.057936906814575195, 0.05755186080932617]
