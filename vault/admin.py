from django.contrib import admin
from .models import EncryptedFile, FileAccessLog

@admin.register(EncryptedFile)
class EncryptedFileAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'file_type', 'file_size', 'created_at')
    list_filter = ('file_type', 'created_at', 'user')
    search_fields = ('original_filename', 'user__username')
    readonly_fields = ('salt', 'iv', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

@admin.register(FileAccessLog)
class FileAccessLogAdmin(admin.ModelAdmin):
    list_display = ('file', 'user', 'access_type', 'timestamp', 'ip_address')
    list_filter = ('access_type', 'timestamp', 'user')
    search_fields = ('file__original_filename', 'user__username', 'ip_address')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
