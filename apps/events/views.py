
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Event
from .serializers import (
    EventSerializer, 
    EventCreateSerializer, 
    EventDetailSerializer,
    EventWithPaymentSerializer
)
from ..core.permissions import IsOwnerOrReadOnly
from rest_framework.pagination import PageNumberPagination

from django_filters import rest_framework as django_filters
from rest_framework import viewsets, permissions, status, filters
from django_filters.rest_framework import DjangoFilterBackend

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class EventFilter(django_filters.FilterSet):
    # Use django_filters here, not filters
    start_date = django_filters.DateTimeFilter(field_name='date', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='date', lookup_expr='lte')
    
    class Meta:
        model = Event
        fields = ['privacy', 'created_by', 'start_date', 'end_date']

class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing events
    """
    queryset = Event.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['privacy', 'created_by']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['date', 'created_at']
    pagination_class = StandardResultsSetPagination
    filterset_class = EventFilter
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on the action
        """
        if self.action == 'create':
            # Check if payment parameters are included
            if 'payment_link' in self.request.data:
                return EventWithPaymentSerializer
            return EventCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return EventDetailSerializer
        return EventSerializer
    
    def get_queryset(self):
        """
        Filter events based on privacy settings and user authentication
        """
        queryset = Event.objects.all()
        
        # If user is not authenticated, show only public events
        if not self.request.user.is_authenticated:
            return queryset.filter(privacy='PUBLIC')
        
        # If user is authenticated, show:
        # 1. Public events
        # 2. Private events created by the user
        # 3. Semi-private events (business logic for semi-private can be expanded)
        return queryset.filter(
            privacy='PUBLIC'
        ) | queryset.filter(
            created_by=self.request.user
        ) | queryset.filter(
            privacy='SEMI_PRIVATE'
        )
    
    def create(self, request, *args, **kwargs):
        """
        Create a new event and return the event with a shareable link
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Get the full event details
        event = serializer.instance
        event_detail = EventDetailSerializer(event, context={'request': request})
        
        # Generate a shareable link (in real app, might use a shortener or encryption)
        shareable_link = f"/events/{event.id}"
        
        return Response({
            'status': 'success',
            'message': 'Event created successfully',
            'event': event_detail.data,
            'shareable_link': shareable_link
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def share(self, request, pk=None):
        """
        Generate shareable link/QR code for an event
        """
        event = self.get_object()
        
        # For a real implementation, could generate short links, QR code data, etc.
        shareable_data = {
            'link': f"/events/{event.id}",
            'title': event.title,
            'date': event.date,
            'qr_code_data': f"invike://events/{event.id}" # Format for mobile deep linking
        }
        
        return Response({
            'status': 'success',
            'sharing_options': shareable_data
        })
    
    @action(detail=True, methods=['get'])
    def guests(self, request, pk=None):
        """
        Get all guests for an event
        This is a placeholder - we'll implement this properly in the RSVP module
        """
        event = self.get_object()
        
        # Check permissions - only allow host or guests to see guest list
        if request.user != event.created_by and event.privacy == 'PRIVATE':
            # In a real implementation, we would check if the user is in the guest list
            # For now, we'll just reject if it's a private event and user is not the host
            return Response({
                'status': 'error',
                'message': 'You do not have permission to view the guest list'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Placeholder for guest list data that would come from RSVP model
        # In the real implementation, this would query the RSVP model
        guests = [
            {'id': '1', 'name': 'Guest One', 'status': 'Yes'},
            {'id': '2', 'name': 'Guest Two', 'status': 'Maybe'},
            {'id': '3', 'name': 'Guest Three', 'status': 'No'},
        ]
        
        return Response({
            'status': 'success',
            'event_id': str(event.id),
            'total_guests': len(guests),
            'guests': guests
        })
    
    @action(detail=True, methods=['get'])
    def export_guests(self, request, pk=None):
        """
        Export guest list as CSV
        This is a placeholder - full implementation would be in the RSVP module
        """
        event = self.get_object()
        
        # Only allow the host to export the guest list
        if request.user != event.created_by:
            return Response({
                'status': 'error',
                'message': 'Only the event host can export the guest list'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # In real implementation, this would generate a CSV file
        # For now, we'll return a success message
        return Response({
            'status': 'success',
            'message': 'Guest list export initiated',
            'download_link': f"/api/events/{event.id}/export_csv"
        })
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    

    # Add this to the existing EventViewSet class

    @action(detail=True, methods=['get'])
    def guest_list(self, request, pk=None):
        """
        Get the complete guest list with RSVP and payment information
        """
        event = self.get_object()
        
        # Only the event host should access this
        if event.created_by != request.user:
            return Response({
                'status': 'error',
                'message': 'Only the event host can access the guest list'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get all RSVPs for this event
        from apps.rsvp.models import RSVP
        rsvps = RSVP.objects.filter(event=event)
        
        # Enhance with payment information
        from apps.payments.models import Payment
        
        result = []
        for rsvp in rsvps:
            payment = Payment.objects.filter(
                event=event,
                user=rsvp.user
            ).first()
            
            payment_status = "NOT_STARTED"
            if payment:
                payment_status = payment.status
            
            result.append({
                'user': {
                    'id': str(rsvp.user.id),
                    'name': rsvp.user.name,
                    'email': rsvp.user.email,
                    'avatar': rsvp.user.avatar
                },
                'rsvp': {
                    'status': rsvp.status,
                    'plus_ones': rsvp.plus_ones,
                    'is_approved': rsvp.is_approved,
                    'created_at': rsvp.created_at
                },
                'payment': {
                    'status': payment_status,
                    'amount': payment.amount if payment else None,
                    'manually_confirmed': payment.manually_confirmed if payment else False,
                    'confirmation_notes': payment.confirmation_notes if payment else None,
                    'created_at': payment.created_at if payment else None
                }
            })
        
        return Response({
            'status': 'success',
            'guests': result
        })

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on the action
        """
        if self.action == 'create':
            # Check if payment parameters are included
            if 'payment_link' in self.request.data:
                return EventWithPaymentSerializer
            return EventCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return EventDetailSerializer
        return EventSerializer

