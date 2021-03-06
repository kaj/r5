from blog.models import Post, Update, Image
from django.core.management.base import BaseCommand
from io import open
from optparse import make_option
from os import mkdir, path
from lxml.etree import fromstring, tostring

def ready_to_save(content):
    '''Make content ready to save.

    Image refs (slugs) are replaced with the full path.'''
    dom = fromstring(u'<article>%s</article>' % content)
    for figure in dom.iterfind('.//figure'):
        ref = figure.get('ref')
        try:
            figure.set('ref', Image.objects.get(ref=ref).sourcename)
        except:
            print('Image %s not found' % ref)
            continue

    return u''.join(tostring(x, encoding=str) for x in dom.iterchildren())
    
class Command(BaseCommand):
    help = 'Save content in semi-html format'

    def add_arguments(self, parser):
        parser.add_argument('--year', dest='year', type=int,
                            help='Include posts from this year only')

    def handle(self, **options):
        self.verbosity = int(options['verbosity'])
        posts = Post.objects
        if options['year']:
            year = options['year']
            self.msg(0, "Dumping content from %s", year)
            posts = posts.filter(posted_time__year=year)
        else:
            self.msg(0, "Dumping all content")
        for post in posts.all():
            filename = 'dump' + post.get_absolute_url() + '.html'
            self.msg(1, "Should save to %s", filename)
            if not path.exists(path.dirname(filename)):
                mkdir(path.dirname(filename))
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(u'<html lang="%s">\n' % post.lang)
                f.write(u'  <head>\n')
                f.write(u'    <title>' + post.title + '</title>\n')
                # TODO Handle the zone better?
                f.write(u'    <pubdate>%sZ</pubdate>\n' %
                        post.posted_time.isoformat())
                for tag in post.tags.all().order_by('name'):
                    f.write(u'    <tag>%s</tag>\n' % tag)
                if post.abstract:
                    f.write(u'    <abstract>\n      %s\n    </abstract>\n' %
                            ready_to_save(post.abstract))
                for update in post.update_set.exclude(note=''):
                    f.write(u'    <update date="%sZ">\n      %s\n    </update>\n' %
                            (update.time.isoformat(), update.note))
                f.write(u'  </head>\n\n')
                f.write(u'  ' + ready_to_save(post.content) + '\n')
                f.write(u'</html>\n')
    
    def msg(self, level, message, *args):
        if self.verbosity > level:
            self.stdout.write(message % args)
