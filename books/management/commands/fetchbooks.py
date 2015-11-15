from django.core.management.base import NoArgsCommand
import json
import urllib
from books.models import Author, Book, BookTag
from django.utils.safestring import mark_safe

class Command(NoArgsCommand):
    help = 'Fetch my books from LibraryThing'

    def handle_noargs(self, **options):
        Book.objects.all().delete()
        BookTag.objects.all().delete()
        url = 'https://www.librarything.com/api_getdata.php?userid=kaj&key=w5c54f5e485d879152955168d89&responseType=json&coverheight=100&max=2000&showTags=1'
        data = json.load(urllib.urlopen(url))

        for key, book in data.get('books').items():
            print "Found book %s" % key
            author, _new = Author.objects.get_or_create(
                lt_slug=book.get('author_code'),
                defaults={'name': book.get('author_fl')})
            book_object = Book.objects.create(
                lt_id = key,
                title=book.get('title'),
                author=author,
                cover=book.get('cover'),
                lang = book.get('language_main'),
                rating = int(10 * book.get('rating', 0)),
                )
            book_object.save()
            tags = book.get('tags')
            if tags:
                print "Book is tagged %s" % tags
                book_object.tags.add(*tags)
