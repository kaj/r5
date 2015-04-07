# -*- encoding: utf-8 -*-
from django import forms
from django.conf import settings
from django.forms import ModelForm
from r5comments.models import Comment
from django.utils.translation import ugettext_lazy as _
from httplib import HTTPConnection, HTTPSConnection
from urlparse import urlparse
import re
from django.forms import widgets

from django.forms.utils import ErrorList
class MyErrorList(ErrorList):
    def __unicode__(self):              # __unicode__ on Python 2
        return self.as_divs()
    def as_divs(self):
        if not self: return ''
        return ''.join('<i class="error">&#x2022; %s</i> ' % e for e in self)

class CommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs['error_class'] = MyErrorList
        super(CommentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Comment
        fields = ('post', 'by_name', 'by_email', 'by_url', 'comment')
        widgets = {
            'post': widgets.HiddenInput(),
        }

    bad_names = ('boobs',
                 'cash', 'casinos?', 'cheap', 'cheats?', 'cialis',
                 'cigarettes?', 'cigs',
                 'discounts?', 'download', 'escorts?', 'facebook', 'finance',
                 'followers', 'forex', 'free', 'hack',
                 'infoxesee', 'instagram', 'insurance',
                 'loans?', 'luggisintedge',
                 'marketing', 'movie', 'offinafag', 'ordillaoffips', 'outlet',
                 'pay ?day', 'penis', 'poker', 'praikicky', 'pyncpelay',
                 'reviews?',
                 'sale', 'shemale', 'sex', 'sexchat', 'stereoids',
                 r'tripod\.co\.uk', 'twitter',
                 'webcam', 'viagra', 'video', 'youtube')

    def clean_name(self):
        #super(CommentFormAvoidingSpam, self).clean_name()
        name = self.cleaned_data['name']
        if re.search('(?:^|-|\.|\s)(?:%s)(?:\s|-|\.|$)' % '|'.join(self.bad_names),
                     name, re.IGNORECASE):
            raise forms.ValidationError(_(u'"%s" in a name looks like spam, sorry.') %
                                        name)
        return name

    def clean_by_url(self):
        #super(CommentFormAvoidingSpam, self).clean_url()
        urlstr = self.cleaned_data['by_url']
        if urlstr:
            url = urlparse(urlstr)
            host = re.sub(r'^www\.', '', url.netloc.lower())
            if host in settings.SHORTEN_SITES:
                raise forms.ValidationError(
                    _('Please use an unshortened url.'))

            if host in settings.SPAM_HOSTS:
                raise forms.ValidationError(
                    _(u'I get to much spam from %s, sorry.') % host)

            if url.scheme in ['http', '']:
                con = HTTPConnection(url.netloc)
            elif url.scheme == 'https':
                con = HTTPSConnection(url.netloc)
            else:
                raise forms.ValidationError(
                    _('Please use a http or https url, not %s.') % url.scheme)
            def rel_part(u):
                return u.path + \
                    (';' + u.params if u.params else '') + \
                    ('?' + u.query if u.query else '')
            try:
                con.request('HEAD', rel_part(url))
                resp = con.getresponse()
                resp.read()
            except Exception as err:
                raise forms.ValidationError(
                    _('Failed to check url %(url)s: %(msg)s.') %
                    {'url': urlstr, 'msg': err})
            if resp.status == 200:
                pass
            elif resp.status in [301, 302, 303, 307]:
                target = urlparse(resp.getheader('Location'))
                print "Comment url redirect %s -> %s" \
                    % (url.geturl(), target.geturl())
                if target.netloc.lower() != url.netloc.lower():
                    raise forms.ValidationError(
                        _('Please use a direct url (%(url)s redirects to %(target)s)') %
                        {'url': url.netloc, 'target': target.netloc})
            else:
                raise forms.ValidationError(
                    _('Your url returns %(code)s %(msg)s') %
                    {'code': resp.status, 'msg': resp.reason})

            spamurls = Comment.objects \
                .filter(is_public=False, is_removed=True) \
                .values_list('by_url', flat=True)
            if url in spamurls:
                raise forms.ValidationError(
                    _(u'"%s" is used in spam, sorry.') % urlstr)
        return urlstr

    def as_p(self):
        "Returns this form rendered as HTML <p>s."
        return self._html_output(
            normal_row='<p%(html_class_attr)s>%(label)s <span>%(errors)s%(field)s%(help_text)s</span></p>',
            error_row='%s',
            row_ender='</p>',
            help_text_html=' <i class="helptext">%s</i>',
            errors_on_separate_row=False)
