from django.contrib import admin
from models import *

class CommentAdmin(admin.ModelAdmin):
    list_display = ('by_name', 'by_email', 'by_ip', 'post', 'submit_date',
                    'is_public', 'is_removed')
    date_hierarchy = 'submit_date'
    list_filter = ('is_public', 'is_removed')
    
admin.site.register(Comment, CommentAdmin)
