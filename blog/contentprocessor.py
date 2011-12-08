from django.utils.safestring import mark_safe
from lxml.etree import fromstring, SubElement, tostring

def process_content(content):
    dom = fromstring(u'<article>%s</article>' % content)
    for figure in dom.iterfind('figure'):
        ref = figure.attrib['ref']
        del figure.attrib['ref']
        a = SubElement(figure, 'a', {'href': '%s.jpg' % ref})
        img = SubElement(a, 'img', {'src': '%s.i.jpeg' % ref})
    
    return mark_safe(u''.join(tostring(x, encoding=unicode) for x in dom.iterchildren()))
