from rest_framework import serializers
from .models import Payment
from apps.users.serializers import UserSerializer
from apps.events.serializers import EventSerializer

class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Payment model (list view)
    """
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = (
            'id', 'event', 'user', 'payment_link', 
            'amount', 'description', 'status',
            'manually_confirmed', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

class PaymentLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for adding payment links to events
    """
    event_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Payment
        fields = ('id', 'event_id', 'payment_link', 'amount', 'description')
        read_only_fields = ('id',)
    
    def validate(self, data):
        """
        Ensure the user is the event host
        """
        event_id = data['event_id']
        user = self.context['request'].user
        
        from apps.events.models import Event
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event does not exist")
        
        # Only the event host can add payment links
        if event.created_by != user:
            raise serializers.ValidationError("Only the event host can add payment links")
        
        self.event = event
        
        return data
    
    def create(self, validated_data):
        event_id = validated_data.pop('event_id')
        user = self.context['request'].user
        
        # Create the payment link
        payment = Payment.objects.create(
            event_id=event_id,
            user=user,  # This will be the host in this case
            **validated_data
        )
        
        return payment

class PaymentConfirmationSerializer(serializers.ModelSerializer):
    """
    Serializer for confirming payments
    """
    event_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Payment
        fields = ('id', 'event_id', 'status', 'confirmation_notes')
        read_only_fields = ('id',)
    
    def validate(self, data):
        """
        Validate the payment confirmation
        """
        event_id = data['event_id']
        user = self.context['request'].user
        
        from apps.events.models import Event
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event does not exist")
        
        # Check if a payment already exists for this user and event
        existing_payment = Payment.objects.filter(
            event_id=event_id,
            user=user,
            status__in=['PAID', 'PENDING']
        ).first()
        
        if existing_payment:
            if existing_payment.status == 'PAID':
                raise serializers.ValidationError("You have already confirmed payment for this event")
            # If payment exists but is pending, we'll update it instead of creating new
            self.instance = existing_payment
        
        # Find the payment link for this event
        host_payment = Payment.objects.filter(
            event_id=event_id,
            user=event.created_by,
            payment_link__isnull=False
        ).first()
        
        if not host_payment:
            raise serializers.ValidationError("No payment link found for this event")
        
        self.payment_link = host_payment.payment_link
        self.event = event
        
        return data
    
    def create(self, validated_data):
        event_id = validated_data.pop('event_id')
        user = self.context['request'].user
        
        # If we found an existing payment during validation, update it
        if hasattr(self, 'instance') and self.instance:
            self.instance.status = 'PAID'
            self.instance.manually_confirmed = True
            self.instance.confirmation_notes = validated_data.get('confirmation_notes', '')
            self.instance.save()
            return self.instance
        
        # Create a new payment confirmation
        payment = Payment.objects.create(
            event_id=event_id,
            user=user,
            status='PAID',
            manually_confirmed=True,
            payment_link=self.payment_link,  # Reference to the host's payment link
            confirmation_notes=validated_data.get('confirmation_notes', '')
        )
        
        return payment

class PaymentStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for hosts to update payment status
    """
    class Meta:
        model = Payment
        fields = ('status', 'confirmation_notes')
