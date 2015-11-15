from django.db import models
from taggit.managers import TaggableManager
from taggit.models import TagBase, ItemBase

class BookTag(TagBase):
    pass

class TaggedBook(ItemBase):
    tag = models.ForeignKey(BookTag,
                            related_name="%(app_label)s_%(class)s_items")
    content_object = models.ForeignKey('Book')

    @classmethod
    def tags_for(cls, model, instance=None, **extra_filters):
        kwargs = extra_filters or {}
        if instance is not None:
            kwargs.update({
                '%s__content_object' % cls.tag_relname(): instance
            })
            return cls.tag_model().objects.filter(**kwargs)
        kwargs.update({
            '%s__content_object__isnull' % cls.tag_relname(): False
        })
        return cls.tag_model().objects.filter(**kwargs).distinct()

class Author(models.Model):
    lt_slug = models.CharField(max_length=32, unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)

class Book(models.Model):
    """One of my books on LibraryThing."""
    lt_id = models.CharField(max_length=16, unique=True, db_index=True)
    title = models.CharField(max_length=200, db_index=True)
    author = models.ForeignKey(Author, db_index=True)
    cover = models.URLField(null=True, blank=True)
    lang = models.CharField(max_length=3, db_index=True)
    rating = models.PositiveSmallIntegerField(help_text='LT rating times 10',
                                              db_index=True)
    tags = TaggableManager(through=TaggedBook)
