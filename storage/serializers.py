from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    File, 
    Folder, 
    FileShare, 
    FolderShare, 
    ShareLink, 
    ActivityLog
)

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with minimal fields for security."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for activity logs with user details."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'activity_type', 'file', 'folder',
            'ip_address', 'details', 'created_at'
        ]
        read_only_fields = ['ip_address', 'user']


class ShareLinkSerializer(serializers.ModelSerializer):
    """Serializer for generating and managing share links."""
    url = serializers.SerializerMethodField()
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ShareLink
        fields = [
            'id', 'uuid', 'created_by', 'created_at', 'expires_at',
            'password', 'max_downloads', 'download_count', 'is_active',
            'url'
        ]
        read_only_fields = ['uuid', 'created_by', 'download_count']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_url(self, obj):
        """Generate the shareable URL for the link."""
        request = self.context.get('request')
        if request and obj.uuid:
            return request.build_absolute_uri(f'/api/share/{obj.uuid}/')
        return None

    def validate_expires_at(self, value):
        """Validate that expiration date is in the future."""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Expiration date must be in the future."
            )
        return value

    def validate_max_downloads(self, value):
        """Validate maximum downloads is positive."""
        if value and value <= 0:
            raise serializers.ValidationError(
                "Maximum downloads must be a positive number."
            )
        return value


class BaseShareSerializer(serializers.ModelSerializer):
    """Base serializer for sharing functionality."""
    user = UserSerializer(read_only=True)
    user_email = serializers.EmailField(write_only=True)
    
    class Meta:
        abstract = True
        fields = [
            'id', 'user', 'user_email', 'permission',
            'created_at', 'expires_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'is_active']

    def validate_expires_at(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Expiration date must be in the future."
            )
        return value

    def validate_user_email(self, value):
        try:
            user = User.objects.get(email=value)
            # Prevent sharing with yourself
            if user == self.context['request'].user:
                raise serializers.ValidationError(
                    "Cannot share with yourself."
                )
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No user found with this email."
            )


class FileShareSerializer(BaseShareSerializer):
    """Serializer for file sharing."""
    class Meta(BaseShareSerializer.Meta):
        model = FileShare

    def create(self, validated_data):
        email = validated_data.pop('user_email')
        user = User.objects.get(email=email)
        return FileShare.objects.create(
            user=user,
            **validated_data
        )


class FolderShareSerializer(BaseShareSerializer):
    """Serializer for folder sharing."""
    class Meta(BaseShareSerializer.Meta):
        model = FolderShare

    def create(self, validated_data):
        email = validated_data.pop('user_email')
        user = User.objects.get(email=email)
        return FolderShare.objects.create(
            user=user,
            **validated_data
        )


class FileSerializer(serializers.ModelSerializer):
    """Serializer for files with sharing information."""
    owner = UserSerializer(read_only=True)
    shared_with = FileShareSerializer(
        source='fileshare_set',
        many=True,
        read_only=True
    )
    share_links = ShareLinkSerializer(
        many=True,
        read_only=True
    )
    size_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = File
        fields = [
            'id', 'name', 'folder', 'owner', 'file',
            'size', 'size_formatted', 'mime_type',
            'created_at', 'updated_at', 'shared_with',
            'share_links'
        ]
        read_only_fields = ['owner', 'size', 'mime_type']

    def get_size_formatted(self, obj):
        """Return human-readable file size."""
        bytes = obj.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} TB"


class FolderSerializer(serializers.ModelSerializer):
    """Serializer for folders with nested files and sharing information."""
    owner = UserSerializer(read_only=True)
    files = FileSerializer(many=True, read_only=True)
    shared_with = FolderShareSerializer(
        source='foldershare_set',
        many=True,
        read_only=True
    )
    parent_path = serializers.SerializerMethodField()
    
    class Meta:
        model = Folder
        fields = [
            'id', 'name', 'parent', 'owner',
            'created_at', 'updated_at', 'files',
            'shared_with', 'parent_path'
        ]
        read_only_fields = ['owner']

    def get_parent_path(self, obj):
        """Get the full path of parent folders."""
        path = []
        current = obj.parent
        while current:
            path.insert(0, {
                'id': current.id,
                'name': current.name
            })
            current = current.parent
        return path


class BulkShareSerializer(serializers.Serializer):
    """Serializer for bulk sharing operations."""
    items = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    user_emails = serializers.ListField(
        child=serializers.EmailField(),
        min_length=1
    )
    permission = serializers.ChoiceField(
        choices=['VIEW', 'EDIT', 'ADMIN'],
        default='VIEW'
    )
    expires_at = serializers.DateTimeField(
        required=False,
        allow_null=True
    )

    def validate_items(self, value):
        """Validate that all items exist and user has permission."""
        request = self.context['request']
        invalid_items = []
        
        for item_id in value:
            try:
                if 'files' in self.context:
                    File.objects.get(
                        id=item_id,
                        owner=request.user
                    )
                else:
                    Folder.objects.get(
                        id=item_id,
                        owner=request.user
                    )
            except (File.DoesNotExist, Folder.DoesNotExist):
                invalid_items.append(item_id)
        
        if invalid_items:
            raise serializers.ValidationError(
                f"Invalid items: {invalid_items}"
            )
        return value

    def validate_user_emails(self, value):
        """Validate that all users exist."""
        invalid_emails = []
        request_user_email = self.context['request'].user.email
        
        for email in value:
            if email == request_user_email:
                raise serializers.ValidationError(
                    f"Cannot share with yourself ({email})"
                )
            if not User.objects.filter(email=email).exists():
                invalid_emails.append(email)
        
        if invalid_emails:
            raise serializers.ValidationError(
                f"Users not found: {invalid_emails}"
            )
        return value

    def validate_expires_at(self, value):
        """Validate expiration date."""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Expiration date must be in the future."
            )
        return value