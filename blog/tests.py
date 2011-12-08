"""
Test the blog module
"""

from django.test import TestCase
from contentprocessor import *

class ContentProcessorTest(TestCase):

    def test_process_simple(self):
        INPUT = '\n'.join([
                '<figure class="image sidebar" ref="foo" />',
                '<p>Lorem ipsum.</p>'
                ])
        
        EXPECTED = '\n'.join([
                '<figure class="image sidebar"><a href="foo.jpg"><img src="foo.i.jpeg"/></a></figure>',
                '<p>Lorem ipsum.</p>'
                ])
        
        self.assertEqual(EXPECTED, process_content(INPUT))


#def t():
#    process_content_etree(INPUT)

# timeit.repeat(stmt=t, number=1000)
# [0.05785393714904785, 0.057936906814575195, 0.05755186080932617]
