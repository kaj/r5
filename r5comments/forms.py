from django import forms
from django.contrib.comments.forms import CommentForm
from django.utils.translation import ugettext_lazy as _
import re

class CommentFormAvoidingSpam(CommentForm):
    bad_names = ('pay ?day', 'loans?', 'finance', 'cigarettes')

    def clean_name(self):
        #super(CommentFormAvoidingSpam, self).clean_name()
        name = self.cleaned_data['name']
        if re.search('(?:^|\s)(?:%s)(?:\s|$)' % '|'.join(self.bad_names),
                     name, re.IGNORECASE):
            raise forms.ValidationError(_(u'"%s" looks like spam, sorry.') %
                                        name)
        return name
