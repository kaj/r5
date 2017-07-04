from blog.models import Image
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'List known images'

    def handle(self, **options):
        for img in Image.objects.order_by('sourcename').all():
            print(img.sourcename)
