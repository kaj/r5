from django.utils.safestring import mark_safe
from lxml.etree import fromstring, SubElement, tostring

def process_content(content, images):
    dom = fromstring(u'<article>%s</article>' % content)
    for figure in dom.iterfind('figure'):
        ref = figure.attrib['ref']
        del figure.attrib['ref']
        info = images.get(ref)
        title = figure.xpath('title')
        a = SubElement(figure, 'a', {'href': info.large})
        if len(title) == 1:
            a.attrib['title'] = tostring(title[0], method='text', encoding=unicode, with_tail=False)
            figure.remove(*title)
        img = SubElement(a, 'img', {'src': info.icon,
                                    'width': info.iwidth,
                                    'height': info.iheight})
    
    return mark_safe(u''.join(tostring(x, encoding=unicode) for x in dom.iterchildren()))
