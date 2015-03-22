from django.contrib import admin
from models import *

def mod_public(modeladmin, request, queryset):
    queryset.update(is_public=True)
mod_public.short_description = "Moderate to public"

def mod_remove(modeladmin, request, queryset):
    queryset.update(is_removed=True)
mod_remove.short_description = "Moderate to removed"

class CommentAdmin(admin.ModelAdmin):
    list_display = ('by_name', 'submit_date', 'by_email', 'by_ip', 'post',
                    'is_public', 'is_removed', 'by_url')
    date_hierarchy = 'submit_date'
    list_filter = ('is_public', 'is_removed')
    actions = [mod_public, mod_remove]

admin.site.register(Comment, CommentAdmin)
