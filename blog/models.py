from autoslug.fields import AutoSlugField
from django.db import models
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from blog.contentprocessor import process_content
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from lxml.etree import fromstring as str2dom, tostring as dom2str
from os import path
from re import sub

class TaggedPost(TaggedItemBase):
    content_object = models.ForeignKey('Post')

class Post(models.Model):
    
    posted_time = models.DateTimeField(null=True, blank=True, db_index=True)
    slug = AutoSlugField(populate_from='title', db_index=True,
                         unique_with=('posted_time__year', 'lang'))

    title = models.CharField(max_length=200)
    abstract = models.TextField(blank=True)
    content = models.TextField()
    frontimage = models.TextField(blank=True)
    lang = models.CharField(max_length=2, db_index=True)
    tags = TaggableManager(through=TaggedPost)
    
    class Meta:
        ordering = ['-posted_time']

    @property
    def year(self):
        return self.posted_time.year

    @property
    def pub_comments(self):
        return self.comment_set.filter(is_public=True, is_removed=False).all()

    def abstract_output(self):
        return process_content(self.abstract, Image.objects, lang=self.lang)
    
    def abstract_text(self):
        return sub('\s+', ' ', strip_tags(self.abstract))
    
    def content_output(self):
        return process_content(self.content, Image.objects,
                               '/%d/' % self.posted_time.year,
                               lang=self.lang)

    def frontimage_output(self):
        return process_content(self.frontimage, Image.objects, lang=self.lang)
    
    def __unicode__(self):
        year = self.posted_time.year if self.posted_time else 'unposted'
        return u'%s (%s)' % (html2cleanstr(self.title), year)
    
    def get_absolute_url(self):
        if self.posted_time:
            return "/%d/%s.%s" % (self.posted_time.year, self.slug, self.lang)
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

    @property
    def year(self):
        '''Linking year, not update year.  I.e. year of the post.'''
        return self.post.year

    @property
    def slug(self):
        return self.post.slug
    
    def __unicode__(self):
        return u'Update %s to %s' % (self.time, self.post)
    
    def note_output(self):
        return process_content(self.note, Image.objects, lang=self.lang)

    def get_absolute_url(self):
        return self.post.get_absolute_url()

class Image(models.Model):
    ref = models.CharField(max_length=50, db_index=True, unique=True)
    sourcename = models.CharField(max_length=100, db_index=True, unique=True)
    orig_width = models.IntegerField()
    orig_height = models.IntegerField()
    mimetype = models.CharField(max_length=50)
    
    ICON_MAX = 200
    LARGE_MAX = 900

    def save(self, *args, **kwargs):
        if not self.ref:
            self.ref, x, y = path.basename(self.sourcename) \
                                 .lower().partition('.')
        super(Image, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return u'<Image from %s>' % self.sourcename

    def get_absolute_url(self):
        return reverse('image_view', args=[self.ref])

    @property
    def large(self):
        return self.get_absolute_url()
    
    @property
    def icon(self):
        return reverse('image_small', args=[self.ref])
    
    def scaled_size(self, limit):
        factor = min(1, # Don't scale up!
                     float(limit) / self.orig_width,
                     float(limit) / self.orig_height)
        return (int(round(self.orig_width * factor)),
                int(round(self.orig_height * factor)))
    
    @property
    def is_small(self):
        return self.orig_width <= self.ICON_MAX and self.orig_height <= self.ICON_MAX
    
    @property
    def iwidth(self):
        return self.scaled_size(self.ICON_MAX)[0]
    
    @property
    def iheight(self):
        return self.scaled_size(self.ICON_MAX)[1]
    
    @property
    def width(self):
        return self.scaled_size(self.LARGE_MAX)[0]
    
    @property
    def height(self):
        return self.scaled_size(self.LARGE_MAX)[1]

def html2cleanstr(html):
    """ Render a (partial) html document to a simple text string """
    dom = str2dom(u'<span>%s</span>' % html)
    return sub('\s+', ' ', dom2str(dom, method='text',
                                   encoding=unicode).strip())
