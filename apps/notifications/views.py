from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification
from .serializers import (
    NotificationSerializer, 
    NotificationCreateSerializer,
    NotificationBatchSerializer
)
from ..core.permissions import IsOwnerOrReadOnly, IsEventHost

class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and managing notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'is_read', 'event']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        """
        Filter notifications to only show the authenticated user's notifications
        """
        return Notification.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on the action
        """
        if self.action == 'create':
            return NotificationCreateSerializer
        elif self.action in ['mark_read', 'mark_all_read']:
            return NotificationBatchSerializer
        return NotificationSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            # Only hosts or staff can create notifications
            permission_classes = [permissions.IsAuthenticated, IsEventHost]
        else:
            # Users can only view their own notifications
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """
        Create notifications for multiple users
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Notifications sent successfully',
            'notification': NotificationSerializer(notification).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='mark-read')
    def mark_read(self, request):
        """
        Mark multiple notifications as read
        """
        serializer = NotificationBatchSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Update all notifications
        notifications = serializer.notifications
        notifications.update(is_read=True)
        
        return Response({
            'status': 'success',
            'message': 'Notifications marked as read',
            'count': len(notifications)
        })
    
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """
        Mark all notifications as read
        """
        count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        
        return Response({
            'status': 'success',
            'message': 'All notifications marked as read',
            'count': count
        })
    
    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """
        Get count of unread notifications
        """
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return Response({
            'status': 'success',
            'unread_count': count
        })