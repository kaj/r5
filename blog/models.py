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
        year = self.posted_time.year if self.posted_time else 'unposted'
        return u'%s (%d)' % (self.title, year)
    
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
        IP('27.98.203.51'),
        IP('31.214.144.137'),
        IP('31.214.145.236'),
        IP('31.214.169.253'),
        IP('46.251.227.3'),
        IP('46.251.237.0/24'),
        IP('59.106.177.23'),
        IP('59.58.137.69'),
        IP('59.58.159.228'),
        IP('64.31.16.0/24'),
        IP('69.162.118.155'),
        IP('69.197.152.207'),
        IP('69.249.157.10'),
        IP('79.142.73.169'),
        IP('79.142.68.103'),
        IP('80.243.19.171'),
        IP('80.243.191.178'),
        IP('83.9.122.87'),
        IP('83.21.223.254'),
        IP('87.234.52.194'),
        IP('91.207.5.130'),
        IP('94.242.214.6'),
        IP('96.26.191.231'),
        IP('98.126.95.98'),
        IP('122.248.240.145'),
        IP('109.73.68.194'),
        IP('109.230.192.0/18'),
        IP('109.230.216.103'),
        IP('112.241.202.112'),
        IP('141.105.65.153'),
        IP('117.26.200.71'),
        IP('173.160.240.155'),
        IP('178.215.87.24'),
        IP('188.92.75.244'),
        IP('188.227.166.154'),
        IP('193.105.210.41'),
        IP('195.78.209.35'),
        IP('202.53.206.129'),
        IP('207.237.20.102'),
        IP('210.101.131.231'),
        IP('210.107.100.251'),
        IP('216.245.209.0/24'),
        )

    def moderate(self, comment, content_object, request):
        addr = IP(request.META['REMOTE_ADDR'])
        return any(addr in net for net in PostCommentModerator.BLACKLIST)

moderator.register(Post, PostCommentModerator)
