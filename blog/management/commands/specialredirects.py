from django.core.management.base import NoArgsCommand
#from django.contrib.redirects.models import Redirect
from readfiles import redirect

class Command(NoArgsCommand):
    help = 'Set up some "special" redirects.'
    
    def handle_noargs(self, **options):
        redirect('/2004/trafik-kaj-s.png', '/static/trafik-kaj-s.png')
        redirect('/2004/trafik-kaj-m.png', '/static/trafik-kaj-m.png')
        redirect('/2004/trafik-kaj.png', '/static/trafik-kaj.png')
        redirect('/2004/trafik-kaj.svg', '/static/trafik-kaj.svg')
        redirect('/favicon.ico', '/static/trafik-kaj-s.png')
        redirect('/2009/naturbanner-3868.jpg', '/static/naturbanner-3868.jpg')
        redirect('/2009/naturbanner-1680.jpg', '/static/naturbanner-1680.jpg')
        redirect('/2009/naturbanner-480.jpg', '/static/naturbanner-480.jpg')
        
        redirect('/tagcloud.en.html', '/tag/')
        redirect('/tagcloud.en', '/tag/')
        redirect('/tagcloud.sv.html', '/tag/')
        redirect('/tagcloud.sv', '/tag/')
        redirect('/tagcloud', '/tag/')
        
        redirect('/bild', '/tag/bild')
        redirect('/bild/', '/tag/bild')
        redirect('/hack', '/tag/hack')
        redirect('/hack/', '/tag/hack')
        redirect('/hack/en.html', '/tag/hack')
        redirect('/hack/en', '/tag/hack')
        redirect('/hack/sv.html', '/tag/hack')
        redirect('/java', '/tag/java')
        redirect('/java/', '/tag/java')
        redirect('/java/?C=M;O=A', '/tag/java')
        redirect('/java/?C=M;O=D', '/tag/java')
        redirect('/rant', '/tag/rant')
        redirect('/rant/', '/tag/rant')
        redirect('/rant/en.html', '/tag/rant')
        redirect('/rant/en', '/tag/rant')
        redirect('/rant/sv.html', '/tag/rant')
        redirect('/rant/sv', '/tag/rant')
        
        redirect('/en.html', '/')
        redirect('/en', '/')
        redirect('/sv.html', '/')
        redirect('/sv', '/')
        redirect('/items.en.html', '/')
        redirect('/items.en', '/')
        redirect('/items.sv.html', '/')
        redirect('/items.sv', '/')
        
        redirect('/cv.html', '/about')
        redirect('/cv', '/about')

        redirect('fanatom-sv.xml', 'atom-sv-fandom.xml')
        redirect('/2008/chordlab/chordlab',
                 'https://raw.github.com/kaj/chordlab/master/chordlab')
        redirect('/hack/webredirect?ref=darwinports.com', '/2001/webredirect')

        # And finally some files that just aint there anymore.
        redirect('/rkinit.js', '')
        redirect('/2005/natural.css', '')
        redirect('/2005/rounded/', '')
        redirect('/2006/print.css', '')

