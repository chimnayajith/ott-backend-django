from django.contrib import admin
from dashboard.admin import custom_admin
from .models import User, HistoryItem, WatchlistItem
from django.contrib.auth.admin import UserAdmin
class WatchlistInline(admin.TabularInline):
    model = WatchlistItem
    extra = 0
    readonly_fields = ['content_id', 'content_type', 'timestamp']

    def content_id(self, obj):
        return obj.content.get("id")
    content_id.short_description = 'Content ID'

    def content_type(self, obj):
        return obj.content.get("type")
    content_type.short_description = 'Content Type' 
    
    def get_fields(self, request, obj=None):
        return ['content_id', 'content_type', 'timestamp']

class HistoryInline(admin.TabularInline):
    model = HistoryItem
    extra = 0
    readonly_fields = ['content_id', 'content_type', 'timestamp']

    def content_id(self, obj):
        return obj.content.get("id")
    content_id.short_description = 'Content ID'

    def content_type(self, obj):
        return obj.content.get("type")
    content_type.short_description = 'Content Type' 
    
    def get_fields(self, request, obj=None):
        return ['content_id', 'content_type', 'timestamp']
class UserManagement(UserAdmin):
    inlines = [WatchlistInline, HistoryInline]
    list_display = ('email', 'username','country' , 'date_joined','last_login','is_superuser')
    search_fields = ('email', 'username','country')
    readonly_fields = ('date_joined','last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

custom_admin.register(User, UserManagement)
