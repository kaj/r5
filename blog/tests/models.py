# -*- encoding: utf-8 -*-
"""
Test blog models
"""
from django.test import TestCase
from datetime import datetime
from blog.models import Post

class PostTest(TestCase):
    
    def test_clean_unicode(self):
        post = Post(posted_time = datetime(2013, 11, 14, 12, 25),
                    title = '  <em>Foo</em>\n\t&lt; bar\n\t',
                    lang = 'sv',
                    content = '<p>Foo</p>')
        self.assertEqual(u'Foo < bar (2013)', u'%s' % post)
