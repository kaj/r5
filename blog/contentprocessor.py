from django.utils.safestring import mark_safe
from lxml.etree import fromstring, Element, SubElement, tostring

def process_content(content, images):
    dom = fromstring(u'<article>%s</article>' % content)
    for figure in dom.iterfind('.//figure'):
        ref = figure.attrib['ref']
        del figure.attrib['ref']
        try:
            info = images.get(ref=ref)
        except:
            figure.text = ' (image not found) '
            print 'Image %s not found' % ref
            continue
        title = figure.xpath('title')
        a = Element('a', {'href': info.large})
        figure.insert(0, a)
        if len(title) == 1:
            a.attrib['title'] = tostring(title[0], method='text', encoding=unicode, with_tail=False)
            figure.remove(*title)
        img = SubElement(a, 'img', {'src': info.icon,
                                    'width': str(info.iwidth),
                                    'height': str(info.iheight)})
    
    return mark_safe(u''.join(tostring(x, encoding=unicode) for x in dom.iterchildren()))
