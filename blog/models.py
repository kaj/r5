from django.db import models
from autoslug.fields import AutoSlugField

class Post(models.Model):
    
    posted_time = models.DateTimeField(null=True, blank=True, db_index=True)
    slug = AutoSlugField(populate_from='title', db_index=True,
                         unique_with='posted_time__month')

    title = models.CharField(max_length=200)
    abstract = models.TextField()
    content = models.TextField()
    lang = models.CharField(max_length=2)
    
    class Meta:
        ordering = ['-posted_time']
    
    def get_absolute_url(self):
        if self.posted_time:
            return "/%d/%s" % (self.posted_time.year, self.slug)
        else:
            return "/%s" % self.slug
