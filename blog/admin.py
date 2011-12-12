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
    list_display = ('posted_time', 'slug', 'lang', 'title')
    list_filter = ('lang', )
    date_hierarchy = 'posted_time'
    inlines = (UpdatesInline,)

    def formfield_for_dbfield(self, db_field, **kwargs):
        """Override to get smaller ingress field."""
        field = super(PostAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)
        if db_field.name == 'abstract':
            field.widget.attrs['rows'] = 5
        elif db_field.name == 'frontimage':
            field.widget.attrs['rows'] = 3;
        return field

admin.site.register(Post, PostAdmin)

admin.site.register(Image)
