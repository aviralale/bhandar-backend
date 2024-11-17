from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    ShareLink, ActivityLog, FileShare, FolderShare,
    Folder, File
)

@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'resource_link', 'created_by', 'created_at', 
                   'expires_at', 'download_count', 'is_active', 'is_valid_status')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('uuid', 'created_by__username', 'file__name', 'folder__name')
    readonly_fields = ('uuid', 'download_count')
    
    def resource_link(self, obj):
        if obj.file:
            return obj.file.name
        return obj.folder.name
    resource_link.short_description = 'Shared Resource'
    
    def is_valid_status(self, obj):
        is_valid = obj.is_valid()
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if is_valid else 'red',
            'Valid' if is_valid else 'Invalid'
        )
    is_valid_status.short_description = 'Valid'

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'activity_type', 'resource_name', 'ip_address')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'ip_address', 'file__name', 'folder__name')
    readonly_fields = ('created_at',)
    
    def resource_name(self, obj):
        if obj.file:
            return f"File: {obj.file.name}"
        elif obj.folder:
            return f"Folder: {obj.folder.name}"
        return "-"
    resource_name.short_description = 'Resource'

@admin.register(FileShare)
class FileShareAdmin(admin.ModelAdmin):
    list_display = ('file', 'user', 'permission', 'created_at', 'expires_at', 'is_active')
    list_filter = ('permission', 'is_active', 'created_at', 'expires_at')
    search_fields = ('file__name', 'user__username')
    raw_id_fields = ('file', 'user')

@admin.register(FolderShare)
class FolderShareAdmin(admin.ModelAdmin):
    list_display = ('folder', 'user', 'permission', 'created_at', 'expires_at', 'is_active')
    list_filter = ('permission', 'is_active', 'created_at', 'expires_at')
    search_fields = ('folder__name', 'user__username')
    raw_id_fields = ('folder', 'user')

class FileInline(admin.TabularInline):
    model = File
    extra = 0
    fields = ('name', 'size', 'mime_type', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'parent', 'created_at', 'file_count')
    list_filter = ('created_at', 'owner')
    search_fields = ('name', 'owner__username', 'description')
    raw_id_fields = ('parent', 'owner')
    inlines = [FileInline]
    
    def file_count(self, obj):
        return obj.file_set.count()
    file_count.short_description = 'Files'

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'folder', 'owner', 'size_display', 'mime_type', 
                   'created_at', 'share_count')
    list_filter = ('mime_type', 'created_at')
    search_fields = ('name', 'owner__username', 'folder__name')
    raw_id_fields = ('folder', 'owner')
    
    def size_display(self, obj):
        """Convert size to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if obj.size < 1024:
                return f"{obj.size:.1f} {unit}"
            obj.size /= 1024
        return f"{obj.size:.1f} TB"
    size_display.short_description = 'Size'
    
    def share_count(self, obj):
        return obj.shared_users.count()
    share_count.short_description = 'Shares'