from django.contrib import admin
from models import *

class UpdatesInline(admin.TabularInline):
    model = Update
    extra = 1

    def formfield_for_dbfield(self, db_field, **kwargs):
        """Override to get smaller ingress field."""
        field = super(UpdatesInline, self).formfield_for_dbfield(
            db_field, **kwargs)
        if db_field.name == 'note':
            field.widget.attrs['rows'] = 4
        return field

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'posted_time', 'slug')
    search_fields = ('title', 'slug', 'abstract', 'content')
    fields = (('title', 'slug'), ('lang', 'posted_time'), 'tags',
              ('abstract', 'frontimage'), 'content')
    readonly_fields = ('slug',)
    list_filter = ('lang', )
    date_hierarchy = 'posted_time'
    inlines = (UpdatesInline,)

    def formfield_for_dbfield(self, db_field, **kwargs):
        """Override to get smaller ingress field."""
        field = super(PostAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)
        if db_field.name in ('abstract', 'frontimage'):
            print field.widget.attrs
            field.widget.attrs['rows'] = 4
            field.widget.attrs['cols'] = 60
            field.widget.attrs['class'] = None
        return field

admin.site.register(Post, PostAdmin)

class ImageAdmin(admin.ModelAdmin):
    list_display = ('ref', 'sourcename', 'orig_width', 'orig_height')

admin.site.register(Image, ImageAdmin)
