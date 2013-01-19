# no models in this app
# But here is a moderator class and the line that registers that.
from django.contrib.comments.moderation import CommentModerator, moderator
from django.contrib.comments.models import Comment
from IPy import IP
from blog.models import Post

class PostCommentModerator(CommentModerator):
    """Moderator for comments to Posts."""
    email_notification = True
    
    def moderate(self, comment, content_object, request):
        spammers = Comment.objects.filter(is_removed=True, is_public=False) \
            .values_list('ip_address', flat=True).distinct()
        return request.META['REMOTE_ADDR'] in spammers

moderator.register(Post, PostCommentModerator)
