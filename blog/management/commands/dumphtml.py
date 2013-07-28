from blog.models import Post, Update, Image
from django.core.management.base import NoArgsCommand
from io import open

class Command(NoArgsCommand):
    help = 'Save content in semi-html format'

    def handle_noargs(self, **options):
        for post in Post.objects.filter(posted_time__year=2013):
            filename = 'dump' + post.get_absolute_url() + '.html'
            print "Should save", filename
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(u'<html lang="%s">\n' % post.lang)
                f.write(u'<head>\n')
                f.write(u'  <title>' + post.title + '</title>\n')
                # TODO Handle the zone better?
                f.write(u'  <pubdate>%sZ</pubdate>\n' %
                        post.posted_time.isoformat())
                for tag in post.tags.all():
                    f.write(u'  <tag>%s</tag>\n' % tag)
                if post.abstract:
                    f.write(u'  <abstract>\n    %s\n  </abstract>\n' %
                            post.abstract)
                for update in post.update_set.exclude(note=''):
                    f.write(u'  <update date="%sZ">\n    %s\n  </update>\n' %
                            (update.time.isoformat(), update.note))
                f.write(u'</head>\n')
                f.write(u'<body>\n  ' + post.content + '\n')
                f.write(u'</body>\n')
                f.write(u'</html>\n')
