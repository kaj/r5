from django.core.management.base import BaseCommand
from r5comments.models import Comment
from blog.models import Post
from django.conf import settings
import json
from sys import stdout
import re

class Command(BaseCommand):
    help = "Write comments to json dump"

    def handle(self, **options):
        def tojson(comment):
            d = dict((k, getattr(comment, k))
                     for k in ['by_name', 'by_email', 'by_url', 'by_ip', 'comment'])
            on = comment.post
            d['on'] = '/%s/%s.%s' % (on.year, on.slug, on.lang)
            d['date'] = comment.submit_date.isoformat()
            return d
        json.dump(
            [tojson(c) for c in Comment.objects.filter(is_public=False, is_removed=False)],
            stdout,
            indent=2,
        )
        print()
