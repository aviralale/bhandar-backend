from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class SharePermission(models.TextChoices):
    VIEW = 'VIEW', 'View Only'
    EDIT = 'EDIT', 'Edit'
    ADMIN = 'ADMIN', 'Admin'


class ActivityType(models.TextChoices):
    UPLOAD = 'UPLOAD', 'File Upload'
    DOWNLOAD = 'DOWNLOAD', 'File Download'
    SHARE = 'SHARE', 'Share Created'
    UNSHARE = 'UNSHARE', 'Share Revoked'
    MODIFY = 'MODIFY', 'File Modified'
    VIEW = 'VIEW', 'File Viewed'


class ShareLink(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    file = models.ForeignKey('File', null=True, blank=True, on_delete=models.CASCADE)
    folder = models.ForeignKey('Folder', null=True, blank=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    max_downloads = models.IntegerField(null=True, blank=True)
    download_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        if self.max_downloads and self.download_count >=self.max_downloads:
            return False
        return True


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null = True)
    file = models.ForeignKey('File', blank=True, null=True, on_delete=models.SET_NULL)
    folder = models.ForeignKey('Folder', blank=True, null=True, on_delete=models.SET_NULL)
    activity_type = models.CharField(max_length=10, choices=ActivityType.choices)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(null=True)
    details = models.JSONField(default = dict)
    created_at = models.DateTimeField(auto_now_add=True)


class BaseSharingModel(models.Model):
    permission = models.CharField(
        max_length=10,
        choices=SharePermission.choices,
        default=SharePermission.VIEW,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class FileShare(BaseSharingModel):
    file = models.ForeignKey('File', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('file', 'user')


class FolderShare(BaseSharingModel):
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('folder', 'user')


class Folder(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null = True, blank = True, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shared_users = models.ManyToManyField(
        User,
        through='FolderShare',
        related_name='shared_folders'
    )

    class Meta:
        unique_together = ('name','parent', 'owner')


class File(models.Model):
    name = models.CharField(max_length=255)
    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_files')
    file = models.FileField(upload_to='files/%Y/%m/%d')
    size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shared_users = models.ManyToManyField(
        User,
        through='FileShare',
        related_name='shared_files'
    )

    class Meta:
        unique_together = ('name','folder', 'owner')