from autoslug.fields import AutoSlugField
from django.contrib.comments.moderation import CommentModerator, moderator
from django.db import models
from taggit.managers import TaggableManager
from IPy import IP

class Post(models.Model):
    
    posted_time = models.DateTimeField(null=True, blank=True, db_index=True)
    slug = AutoSlugField(populate_from='title', db_index=True,
                         unique_with=('posted_time__month', 'lang'))

    title = models.CharField(max_length=200)
    abstract = models.TextField(blank=True)
    content = models.TextField()
    frontimage = models.TextField(blank=True)
    lang = models.CharField(max_length=2)
    tags = TaggableManager()
    
    class Meta:
        ordering = ['-posted_time']

    def __unicode__(self):
        return u'%s (%d)' % (self.title, self.posted_time.year)
    
    def get_absolute_url(self):
        if self.posted_time:
            return "/%d/%s" % (self.posted_time.year, self.slug)
        else:
            return "/%s" % self.slug

class Update(models.Model):
    
    post = models.ForeignKey(Post)
    time = models.DateTimeField(db_index=True)

    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-time']

    @property
    def lang(self):
        return self.post.lang

    def get_absolute_url(self):
        return self.post.get_absolute_url()

class PostCommentModerator(CommentModerator):
    """Moderator for comments to Posts."""
    email_notification = True

    BLACKLIST = (
        IP('31.214.145.236'),
        IP('46.251.227.3'),
        IP('46.251.237.188'),
        IP('64.31.16.114'),
        IP('69.162.118.155'),
        IP('80.243.19.171'),
        IP('83.9.122.87'),
        IP('91.207.5.130'),
        IP('98.126.95.98'),
        IP('109.230.192.0/18'),
        IP('193.105.210.41'),
        IP('216.245.209.0/24'),
        )

    def moderate(self, comment, content_object, request):
        addr = IP(request.META['REMOTE_ADDR'])
        return any(addr in net for net in PostCommentModerator.BLACKLIST)

moderator.register(Post, PostCommentModerator)
