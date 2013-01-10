from django import forms
from django.contrib.comments.forms import CommentForm
from django.contrib.comments.models import Comment
from django.utils.translation import ugettext_lazy as _
import re

class CommentFormAvoidingSpam(CommentForm):
    bad_names = ('casino', 'cialis', 'cigarettes', 'escorts?', 'finance',
                 'infoxesee', 'loans?', 'luggisintedge', 'offinafag',
                 'ordillaoffips', 'pay ?day', 'praikicky', 'pyncpelay',
                 'viagra')

    def clean_name(self):
        #super(CommentFormAvoidingSpam, self).clean_name()
        name = self.cleaned_data['name']
        if re.search('(?:^|-|\.|\s)(?:%s)(?:\s|-|\.|$)' % '|'.join(self.bad_names),
                     name, re.IGNORECASE):
            raise forms.ValidationError(_(u'"%s" looks like spam, sorry.') %
                                        name)
        return name

    def clean_url(self):
        # Note: the form field is called url, but the model field is user_url.
        #super(CommentFormAvoidingSpam, self).clean_url()
        url = self.cleaned_data['url']
        if url:
            if re.match('^https?://(bit.ly|is.gd|tinyurl.com)/.*', url, re.IGNORECASE):
                raise forms.ValidationError(
                    _('Please use an unshortened url.'))
            spamurls = Comment.objects \
                .filter(is_public=False, is_removed=True) \
                .values_list('user_url', flat=True)
            if url in spamurls:
                raise forms.ValidationError(
                    _(u'"%s" is used in spam, sorry.') % url)
        return url
