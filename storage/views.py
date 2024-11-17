from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ActivityType, ShareLink, Folder
from .serializers import ShareLinkSerializer, FolderSerializer

class SharePermissionMixin:
    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.owner != request.user:
                share = obj.shared_users.through.objects.filter(
                    user=request.user,
                    **{f'{obj._meta.model_name.lower()}': obj}
                ).first()
                if not share or share.permission not in ['EDIT', 'ADMIN']:
                    self.permission_denied(request)

class BulkShareMixin:
    @action(detail=False, methods=['post'])
    def bulk_share(self, request):
        items = request.data.get('items', [])
        users = request.data.get('users', [])
        permission = request.data.get('permission', 'VIEW')
        expires_at = request.data.get('expires_at')

        share_results = []
        for item_id in items:
            item = self.queryset.get(id=item_id)
            for user_id in users:
                try:
                    share = item.shared_users.through.objects.create(
                        **{self.share_model_field: item},
                        user_id=user_id,
                        permission=permission,
                        expires_at=expires_at
                    )
                    share_results.append({
                        'item_id': item_id,
                        'user_id': user_id,
                        'status': 'success'
                    })
                except Exception as e:
                    share_results.append({
                        'item_id': item_id,
                        'user_id': user_id,
                        'status': 'error',
                        'message': str(e)
                    })

        return Response(share_results)

class FileViewSet(BulkShareMixin, SharePermissionMixin, viewsets.ModelViewSet):
    share_model_field = 'file'

    @action(detail=True, methods=['post'])
    def create_share_link(self, request, pk=None):
        file = self.get_object()
        serializer = ShareLinkSerializer(data=request.data)
        
        if serializer.is_valid():
            share_link = serializer.save(
                file=file,
                created_by=request.user
            )
            
            ActivityLog.objects.create(
                user=request.user,
                file=file,
                activity_type=ActivityType.SHARE,
                ip_address=request.activity_data['ip_address'],
                user_agent=request.activity_data['user_agent'],
                details={'share_link_id': share_link.id}
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def revoke_share(self, request, pk=None):
        file = self.get_object()
        user_id = request.data.get('user_id')
        
        share = file.fileshare_set.filter(user_id=user_id).first()
        if share:
            share.is_active = False
            share.save()
            
            ActivityLog.objects.create(
                user=request.user,
                file=file,
                activity_type=ActivityType.UNSHARE,
                ip_address=request.activity_data['ip_address'],
                user_agent=request.activity_data['user_agent'],
                details={'revoked_user_id': user_id}
            )
            
            return Response({'status': 'share revoked'})
        return Response({'error': 'share not found'}, status=404)
    
class FolderViewSet(SharePermissionMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FolderSerializer

    def get_queryset(self):
        return Folder.objects.filter(
            Q(owner=self.request.user) |
            Q(shared_users=self.request.user)
        ).distinct()

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        folder = self.get_object()
        serializer = FolderShareSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(folder=folder)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)