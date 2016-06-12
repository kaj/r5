from django.core.management.base import NoArgsCommand
from r5comments.models import Comment
from django.conf import settings
from urllib.parse import urlparse
from collections import Counter
from re import sub

class Command(NoArgsCommand):
    help = 'Count hosts I get spam comments for'

    def handle_noargs(self, **options):
        spamurls = Comment.objects \
                          .filter(is_removed=True) \
                          .exclude(by_url='') \
                          .values_list('by_url', flat=True)
        known_spam = settings.SPAM_HOSTS | settings.SHORTEN_SITES
        hosts = Counter()
        for url in spamurls:
            host = sub(r'^www\.', '', urlparse(url).netloc.lower())
            if not host in known_spam:
                hosts[host] += 1

        print('\n'.join("'%s', #%s" % (a, b)
                        for a, b in hosts.most_common(22)))
