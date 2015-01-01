from django import forms
from django.conf import settings
from django.contrib.comments.forms import CommentForm
from django.contrib.comments.models import Comment
from django.utils.translation import ugettext_lazy as _
from httplib import HTTPConnection, HTTPSConnection
from urlparse import urlparse
import re

class CommentFormAvoidingSpam(CommentForm):
    bad_names = ('boobs', 'cash', 'casinos?', 'cialis', 'cigarettes?', 'cigs',
                 'discounts?', 'download', 'escorts?', 'facebook', 'finance',
                 'followers', 'forex', 'free', 'infoxesee', 'instagram',
                 'insurance', 'loans?', 'luggisintedge',
                 'movie', 'offinafag',
                 'ordillaoffips', 'pay ?day', 'poker',
                 'praikicky', 'pyncpelay',
                 'shemale', 'sex', 'sexchat', r'tripod\.co\.uk', 'twitter',
                 'webcam', 'viagra', 'video', 'youtube')

    def clean_name(self):
        #super(CommentFormAvoidingSpam, self).clean_name()
        name = self.cleaned_data['name']
        if re.search('(?:^|-|\.|\s)(?:%s)(?:\s|-|\.|$)' % '|'.join(self.bad_names),
                     name, re.IGNORECASE):
            raise forms.ValidationError(_(u'"%s" in a name looks like spam, sorry.') %
                                        name)
        return name

    def clean_url(self):
        # Note: the form field is called url, but the model field is user_url.
        #super(CommentFormAvoidingSpam, self).clean_url()
        urlstr = self.cleaned_data['url']
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
                    _('Failed to check url %s: %s.') % (urlstr, err))
            if resp.status == 200:
                pass
            elif resp.status in [301, 302, 303, 307]:
                target = urlparse(resp.getheader('Location'))
                print "Got redirect to %s" % (target.geturl())
                if target.netloc.lower() != url.netloc.lower():
                    raise forms.ValidationError(
                        _('Please use a direct url (%s redirects to %s)') %
                        (url.netloc, target.netloc))
            else:
                raise forms.ValidationError(
                    _('Your url returns %s %s') % (resp.status, resp.reason))

            spamurls = Comment.objects \
                .filter(is_public=False, is_removed=True) \
                .values_list('user_url', flat=True)
            if url in spamurls:
                raise forms.ValidationError(
                    _(u'"%s" is used in spam, sorry.') % urlstr)
        return urlstr
