# no models in this app
# But here is a moderator class and the line that registers that.
from django.contrib.comments.moderation import CommentModerator, moderator
from django.contrib.comments.models import Comment
from django.conf import settings
from IPy import IP
from blog.models import Post
from datetime import datetime

class PostCommentModerator(CommentModerator):
    """Moderator for comments to Posts."""
    email_notification = not settings.DEBUG

    def moderate(self, comment, content_object, request):
        # Allow comments from known commenters
        commenters = Comment.objects.filter(is_removed=False, is_public=True) \
            .values_list('ip_address', flat=True).distinct()
        if request.META['REMOTE_ADDR'] in commenters:
            return False
        
        # Moderate comments for old posts
        if (datetime.now() - content_object.posted_time).days > 25:
            return True
        
        # Moderate comments from previous spammers
        spammers = Comment.objects.filter(is_removed=True, is_public=False) \
            .values_list('ip_address', flat=True).distinct()
        return request.META['REMOTE_ADDR'] in spammers

    def email(self, comment, content_object, request):
        '''Dont send email notifications for hidden comments.'''
        if comment.is_public:
            super(PostCommentModerator, self).email(comment, content_object,
                                                    request)

moderator.register(Post, PostCommentModerator)
