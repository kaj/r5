from django.utils.safestring import mark_safe
from lxml.etree import fromstring, SubElement, tostring

def process_content(content):
    dom = fromstring(u'<article>%s</article>' % content)
    for figure in dom.iterfind('figure'):
        ref = figure.attrib['ref']
        del figure.attrib['ref']
        title = figure.xpath('title')
        a = SubElement(figure, 'a', {'href': '%s.jpg' % ref})
        if len(title) == 1:
            a.attrib['title'] = tostring(title[0], method='text', encoding=unicode, with_tail=False)
            figure.remove(*title)
        img = SubElement(a, 'img', {'src': '%s.i.jpeg' % ref})
    
    return mark_safe(u''.join(tostring(x, encoding=unicode) for x in dom.iterchildren()))
