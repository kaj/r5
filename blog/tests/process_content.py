"""
Test the blog module
"""

from django.test import TestCase
from blog.contentprocessor import *


class imageinfo:
    
    def __init__(self, name, width, height, iconsize=200):
        self.large = '%s.jpg' % name
        self.width = width
        self.height = height
        
        self.icon = '%s.i.jpeg' % name
        factor = min(float(iconsize)/width, float(iconsize)/height)
        self.iwidth = int(round(factor * width))
        self.iheight = int(round(factor * height))

class imagecollection:
    def __init__(self, data):
        self.data = data
        
    def get(self, ref):
        return self.data[ref]

class ContentProcessorTest(TestCase):

    def setUp(self):
        self.images = imagecollection({
            'foo': imageinfo('foo', 848, 565),
            })
        
        
    def test_process_simple_figure(self):
        INPUT = '\n'.join([
                '<figure class="image sidebar" ref="foo" />',
                '<p>Lorem ipsum.</p>'
                ])
        
        EXPECTED = '\n'.join([
                '<figure class="image sidebar"><a href="foo.jpg"><img src="foo.i.jpeg" height="133" width="200"/></a></figure>',
                '<p>Lorem ipsum.</p>'
                ])
        
        self.assertEqual(EXPECTED, process_content(INPUT, self.images))

    def test_process_figure_with_title(self):
        INPUT = ''.join([
                '<figure class="image sidebar" ref="foo">',
                '<title>Foo</title>',
                '</figure>',
                '<p>Lorem ipsum.</p>'
                ])
        
        EXPECTED = u''.join([
                '<figure class="image sidebar">',
                '<a href="foo.jpg" title="Foo"><img src="foo.i.jpeg" height="133" width="200"/></a>',
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
                '<title>Foo</title>',
                '<p>This is some kind of caption.</p>',
                '</figure>',
                '<p>Lorem ipsum.</p>'
                ])
        
        EXPECTED = u''.join([
                '<figure class="image sidebar">',
                '<a href="foo.jpg" title="Foo"><img src="foo.i.jpeg" height="133" width="200"/></a>',
                '<p>This is some kind of caption.</p>',
                '</figure>',
                '<p>Lorem ipsum.</p>'
                ])
        
        self.assertEqual(EXPECTED, process_content(INPUT, self.images))

#def t():
#    process_content_etree(INPUT)

# timeit.repeat(stmt=t, number=1000)
# [0.05785393714904785, 0.057936906814575195, 0.05755186080932617]
