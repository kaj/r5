from django.core.management.base import BaseCommand
from r5comments.models import Comment
from blog.models import Post
from django.conf import settings
import json
from sys import stdin
import re

class Command(BaseCommand):
    help = 'Read comments from json dump'

    def handle(self, **options):
        up = re.compile('^/(?P<year>\d+)/(?P<slug>[^.]+)\.(?P<lang>\w+)$')
        def one_comment(obj):
            if 'comment' in obj and 'on' in obj and 'by' in obj:
                m = up.match(obj['on'])
                if m:
                    try:
                        post = Post.objects.get(posted_time__year=m.group('year'),
                                                slug=m.group('slug'),
                                                lang=m.group('lang'))
                    except:
                        print("Post not found:", obj['on'])
                        return None
                    #print "Read a comment on", post
                    c, is_new = Comment.objects.get_or_create(
                        post=post,
                        by_name=obj['by'].get('name'),
                        by_email=obj['by'].get('email'),
                        by_url=obj['by'].get('url'),
                        comment=obj['comment'],
                        submit_date=obj['submit_date'],
                        by_ip=obj['by_ip'],
                        is_public=obj['is_public'],
                        is_removed=obj['is_removed']
                    )
                    c.submit_date = obj['submit_date']
                    c.save()
                    print(c)
                else:
                    print("Non-match target:", obj['on'])
                    exit(1)
                return None
            else:
                return obj
        json.load(stdin, object_hook=one_comment)
        
