"""
Test browsing public pages in the blog app.
"""

from django.test import TestCase
from django.test.client import Client

class SimpleTest(TestCase):
    def test_get_frontpage(self):
        c = Client()
        response = c.get('/')
        self.assertEqual((200, 'text/html; charset=utf-8'),
                         (response.status_code, response['Content-Type']))
