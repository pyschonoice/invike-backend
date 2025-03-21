import csv
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import RSVP
from .serializers import (
    RSVPSerializer, 
    RSVPCreateSerializer, 
    RSVPUpdateSerializer,
    RSVPApprovalSerializer,
    GuestListSerializer
)
from apps.events.models import Event
from ..core.permissions import IsOwnerOrReadOnly, IsEventHost

class RSVPViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing RSVPs
    """
    queryset = RSVP.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'user', 'status', 'is_approved']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        elif self.action in ['approve', 'reject']:
            permission_classes = [permissions.IsAuthenticated, IsEventHost]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on the action
        """
        if self.action == 'create':
            return RSVPCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RSVPUpdateSerializer
        elif self.action in ['approve', 'reject']:
            return RSVPApprovalSerializer
        return RSVPSerializer
    
    def get_queryset(self):
        """
        Filter RSVPs based on user permissions
        """
        queryset = RSVP.objects.all()
        
        # Filter by event if event_id is provided in query params
        event_id = self.request.query_params.get('event_id', None)
        if event_id is not None:
            queryset = queryset.filter(event_id=event_id)
        
        # Filter by user permissions:
        # 1. Users can see their own RSVPs
        # 2. Event hosts can see RSVPs for their events
        if not self.request.user.is_staff:
            user_events = Event.objects.filter(created_by=self.request.user).values_list('id', flat=True)
            queryset = queryset.filter(
                user=self.request.user
            ) | queryset.filter(
                event_id__in=user_events
            )
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create a new RSVP
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Get the full RSVP details
        rsvp = serializer.instance
        rsvp_detail = RSVPSerializer(rsvp, context={'request': request})
        
        return Response({
            'status': 'success',
            'message': 'RSVP created successfully',
            'rsvp': rsvp_detail.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """
        Approve an RSVP (for event hosts)
        """
        rsvp = self.get_object()
        serializer = self.get_serializer(rsvp, data={'is_approved': True}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'status': 'success',
            'message': 'RSVP approved'
        })
    
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        """
        Reject an RSVP (for event hosts)
        """
        rsvp = self.get_object()
        serializer = self.get_serializer(rsvp, data={'is_approved': False}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'status': 'success',
            'message': 'RSVP rejected'
        })

class GuestListViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing guest lists of events
    """
    serializer_class = GuestListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Get the guest list for a specific event
        """
        event_id = self.kwargs.get('event_id')
        
        # Try to get the event
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return RSVP.objects.none()
        
        # Check permissions:
        # 1. Event host can always see the guest list
        # 2. For private events, only approved guests can see the guest list
        # 3. For public/semi-private events, all authenticated users can see the guest list
        if event.created_by == self.request.user:
            # Host can see all RSVPs
            return RSVP.objects.filter(event=event)
        elif event.privacy == 'PRIVATE':
            # For private events, check if the user is an approved guest
            is_approved_guest = RSVP.objects.filter(
                event=event,
                user=self.request.user,
                is_approved=True
            ).exists()
            
            if not is_approved_guest:
                return RSVP.objects.none()
        
        # Return all approved RSVPs for the event
        return RSVP.objects.filter(event=event, is_approved=True)
    
    @action(detail=False, methods=['get'])
    def export(self, request, event_id=None):
        """
        Export guest list as CSV
        """
        # Try to get the event
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the user is the event host
        if event.created_by != request.user:
            return Response({
                'status': 'error',
                'message': 'Only the event host can export the guest list'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get all RSVPs for the event
        queryset = RSVP.objects.filter(event=event)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="guest_list_{event_id}.csv"'
        
        # Write CSV data
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Status', 'Plus Ones', 'Approved', 'RSVP Date'])
        
        for rsvp in queryset:
            writer.writerow([
                rsvp.user.name,
                rsvp.user.email,
                rsvp.get_status_display(),
                rsvp.plus_ones,
                'Yes' if rsvp.is_approved else 'No',
                rsvp.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
