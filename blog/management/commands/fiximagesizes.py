from PIL import Image as PImage
from blog.models import Image
from django.conf import settings
from django.core.management.base import NoArgsCommand
from optparse import make_option
import os

class Command(NoArgsCommand):
    help = 'Find and read content'
    option_list = NoArgsCommand.option_list + (
        make_option('--all', help='Read data for all files',
                    action='store_true', dest='all', default=False),
        )
    
    def handle_noargs(self, **options):
        mime = { 'JPEG': 'image/jpeg',
                 'PNG': 'image/png',
                 }

        # Old more or less junk, but used from static css:
        for parti in ('kds', 'm', 'v', 'c', 'mp', 's', 'fp'):
            img, isnew = Image.objects.get_or_create(
                ref=parti,
                defaults = {
                    'sourcename': 'old/partier/%s.png' % parti,
                    'orig_width': 0,
                    'orig_height': 0})
        
        files = Image.objects
        if not options['all']:
            files = files.filter(orig_width=0, orig_height=0)
        
        for img in files.all():
            filename = os.path.join(settings.IMAGE_FILES_BASE, img.sourcename)
            print "Read %s size from %s" % (img.ref, filename)
            data = PImage.open(filename)
            img.orig_width, img.orig_height = data.size
            img.mimetype = mime[data.format]
            img.save()
