from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment
from .serializers import (
    PaymentSerializer, 
    PaymentLinkSerializer, 
    PaymentConfirmationSerializer,
    PaymentStatusUpdateSerializer
)
from apps.events.models import Event
from ..core.permissions import IsOwnerOrReadOnly, IsEventHost

class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing payments
    """
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'user', 'status', 'manually_confirmed']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['update', 'partial_update']:
            # Use IsEventHost permission for standard update operations
            permission_classes = [permissions.IsAuthenticated, IsEventHost]
        elif self.action == 'add_payment_link':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'confirm_payment':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update_status']:
            permission_classes = [permissions.IsAuthenticated, IsEventHost]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on the action
        """
        if self.action == 'add_payment_link':
            return PaymentLinkSerializer
        elif self.action == 'confirm_payment':
            return PaymentConfirmationSerializer
        elif self.action == 'update_status':
            return PaymentStatusUpdateSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        """
        Filter payments based on user permissions
        """
        queryset = Payment.objects.all()
        
        # Filter by event if event_id is provided in query params
        event_id = self.request.query_params.get('event_id', None)
        if event_id is not None:
            queryset = queryset.filter(event_id=event_id)
        
        # Filter by user permissions:
        # 1. Users can see their own payments
        # 2. Event hosts can see payments for their events
        if not self.request.user.is_staff:
            user_events = Event.objects.filter(created_by=self.request.user).values_list('id', flat=True)
            queryset = queryset.filter(
                user=self.request.user
            ) | queryset.filter(
                event_id__in=user_events
            )
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def add_payment_link(self, request):
        """
        Add a payment link to an event (by host)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Payment link added successfully',
            'payment': PaymentSerializer(payment, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def confirm_payment(self, request):
        """
        Confirm payment for an event (by guest)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Payment confirmed successfully',
            'payment': PaymentSerializer(payment, context={'request': request}).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update payment status (by host)
        """
        payment = self.get_object()
        
        # Check if the user is the event host
        if payment.event.created_by != request.user:
            return Response({
                'status': 'error',
                'message': 'Only the event host can update payment status'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(payment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'status': 'success',
            'message': 'Payment status updated',
            'payment': PaymentSerializer(payment, context={'request': request}).data
        })
    
    @action(detail=False, methods=['get'])
    def event_status(self, request):
        """
        Get payment status for an event
        """
        event_id = request.query_params.get('event_id', None)
        if not event_id:
            return Response({
                'status': 'error',
                'message': 'event_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to get the event
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if event.created_by != request.user and not event.privacy == 'PUBLIC':
            is_participant = Payment.objects.filter(event=event, user=request.user).exists()
            if not is_participant:
                return Response({
                    'status': 'error',
                    'message': 'You do not have permission to view payment status for this event'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Get payment status
        payment_link = Payment.objects.filter(
            event=event, 
            user=event.created_by,
            payment_link__isnull=False
        ).first()
        
        confirmed_payments = Payment.objects.filter(
            event=event,
            status='PAID',
            manually_confirmed=True
        ).count()
        
        pending_payments = Payment.objects.filter(
            event=event,
            status='PENDING'
        ).count()
        
        # Check if the current user has paid
        user_paid = False
        if request.user.is_authenticated:
            user_paid = Payment.objects.filter(
                event=event,
                user=request.user,
                status='PAID'
            ).exists()
        
        return Response({
            'status': 'success',
            'event_id': str(event_id),
            'has_payment_link': payment_link is not None,
            'payment_link': payment_link.payment_link if payment_link else None,
            'amount': payment_link.amount if payment_link else None,
            'confirmed_payments': confirmed_payments,
            'pending_payments': pending_payments,
            'user_has_paid': user_paid
        })

# Add this to the bottom of the file

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])
def payment_webhook(request):
    """
    Webhook endpoint for payment service callbacks.
    This is a placeholder for future payment gateway integration.
    """
    # In a real implementation, you would:
    # 1. Verify webhook signature
    # 2. Extract payment data
    # 3. Update payment status
    # 4. Send notifications
    
    # For now, just return a success response
    return Response({
        'status': 'success',
        'message': 'Payment webhook received'
    })