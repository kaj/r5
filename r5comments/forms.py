from django import forms
from django.contrib.comments.forms import CommentForm
from django.contrib.comments.models import Comment
from django.utils.translation import ugettext_lazy as _
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
        url = self.cleaned_data['url']
        if url:
            host = re.sub(r'^www\.', '', urlparse(url).netloc.lower())
            if host in settings.SHORTEN_SITES:
                raise forms.ValidationError(
                    _('Please use an unshortened url.'))

            if host in settings.SPAM_HOSTS:
                raise forms.ValidationError(
                    _(u'I get to much spam from %s, sorry.') % host)

            spamurls = Comment.objects \
                .filter(is_public=False, is_removed=True) \
                .values_list('user_url', flat=True)
            if url in spamurls:
                raise forms.ValidationError(
                    _(u'"%s" is used in spam, sorry.') % url)
        return url
