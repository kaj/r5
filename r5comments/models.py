from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from IPy import IP
from blog.models import Post
from datetime import datetime

class Comment(models.Model):
    """A comment on a blog.Post.  Optimized by not beeing generic-key."""
    post = models.ForeignKey(Post, db_index=True)
    by_name = models.CharField('Name', max_length=100,
                               help_text=_(u'Your name (or pseudonym).'))
    by_email = models.EmailField('Email', db_index=True,
                                 help_text=_(u'Not published, except as gravatar.'))
    by_url = models.URLField('URL', blank=True, null=True,
                             help_text=_(u'Your homepage / presentation.'))
    comment = models.TextField(help_text=_(u'No formatting, except an empty line is interpreted as a paragraph break.'))
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

if False: '''
class PostCommentModerator(CommentModerator):
    """Moderator for comments to Posts."""
    email_notification = not settings.DEBUG

    def moderate(self, comment, content_object, request):
        # Allow comments from known commenters
        commenters = ContribComment.objects.filter(is_removed=False, is_public=True) \
            .values_list('ip_address', flat=True).distinct()
        if request.META['REMOTE_ADDR'] in commenters:
            return False
        
        # Moderate comments for old posts
        if (datetime.now() - content_object.posted_time).days > 25:
            return True
        
        # Moderate comments from previous spammers
        spammers = ContribComment.objects.filter(is_removed=True, is_public=False) \
            .values_list('ip_address', flat=True).distinct()
        return request.META['REMOTE_ADDR'] in spammers

    def email(self, comment, content_object, request):
        """Dont send email notifications for hidden comments."""
        if comment.is_public:
            super(PostCommentModerator, self).email(comment, content_object,
                                                    request)

moderator.register(Post, PostCommentModerator)
'''
