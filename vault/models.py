from django.db import models
from django.conf import settings

# Create your models here.

class EncryptedFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.BigIntegerField()
    encrypted_path = models.CharField(max_length=255)
    salt = models.BinaryField()
    iv = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Encrypted File'
        verbose_name_plural = 'Encrypted Files'

    def __str__(self):
        return f"{self.original_filename} ({self.user.username})"

class FileAccessLog(models.Model):
    file = models.ForeignKey(EncryptedFile, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20)  # 'upload', 'download', 'delete'
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'File Access Log'
        verbose_name_plural = 'File Access Logs'

    def __str__(self):
        return f"{self.access_type} - {self.file.original_filename} by {self.user.username}"
