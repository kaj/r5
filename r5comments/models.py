from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from IPy import IP
from blog.models import Post
from datetime import datetime

class Comment(models.Model):
    """A comment on a blog.Post.  Optimized by not beeing generic-key."""
    post = models.ForeignKey(Post, db_index=True)
    by_name = models.CharField(_('Name'), max_length=100,
                               help_text=_(u'Your name (or pseudonym).'))
    by_email = models.EmailField(_('Email'), db_index=True,
                                 help_text=_(u'Not published, except as gravatar.'))
    by_url = models.URLField(_('URL'), blank=True, null=True,
                             help_text=_(u'Your homepage / presentation.'))
    comment = models.TextField(_('Comment'),
                               help_text=_(u'No formatting, except that an empty line is interpreted as a paragraph break.'))
    submit_date = models.DateTimeField(db_index=True, auto_now_add=True)
    by_ip = models.GenericIPAddressField(db_index=True, null=True)
    is_removed = models.BooleanField(default=False, db_index=True)
    is_public = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['submit_date']

    def __unicode__(self):
        return u'%s on %s: %s' % (self.by_name, self.post, self.comment[:20])

    def get_absolute_url(self):
        return '%s#c%s' % (self.post.get_absolute_url(), self.id)

    def moderate(self, request):
        self.by_ip = request.META.get('HTTP_X_FORWARDED_FOR') or \
                     request.META.get('REMOTE_ADDR')

        def publicq():
            if Comment.objects. \
               filter(is_removed=False, is_public=True, by_ip=self.by_ip). \
               count() > 0:
                # Known commenter, make it public
                return True

            if (datetime.now() - self.post.posted_time).days > 25:
                # Old post, moderate
                return False
            # Moderate comments from previous spammers
            return Comment.objects.filter(is_removed=True, by_ip=self.by_ip). \
                count() == 0

        self.is_public = publicq()


#    def email(self, comment, content_object, request):
#        """Dont send email notifications for hidden comments."""
#        if comment.is_public:
#            super(PostCommentModerator, self).email(comment, content_object,
#                                                    request)
