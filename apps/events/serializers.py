from rest_framework import serializers
from .models import Event
from apps.users.serializers import UserSerializer

class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for the Event model (list view)
    """
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'date', 'location', 
            'privacy', 'created_by', 'cover_image', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

class EventCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new event
    """
    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'date', 'location', 
            'privacy', 'cover_image', 'latitude', 'longitude'
        )
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        # Set the current user as the creator
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class EventDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the Event model (detail view)
    """
    created_by = UserSerializer(read_only=True)
    payment_information = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'date', 'location', 
            'privacy', 'created_by', 'cover_image', 
            'latitude', 'longitude', 'created_at', 'updated_at',
            'payment_information'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')
    
    def get_payment_information(self, obj):
        """Include payment information if the user has permission to see it"""
        user = self.context['request'].user
        
        # Basic payment info anyone can see
        result = {
            'has_payment': obj.has_payment_link,
        }
        
        # Add payment link if available
        if obj.payment_info:
            result.update({
                'amount': obj.payment_info['amount'],
                'payment_link': obj.payment_info['payment_link'],
                'description': obj.payment_info['description'],
            })
        
        # Add payment stats for the event host
        if user == obj.created_by:
            result.update({
                'payment_stats': obj.payment_stats
            })
        
        # Add user's payment status if they're logged in
        if user.is_authenticated:
            user_paid = obj.payments.filter(
                user=user,
                status='PAID'
            ).exists()
            
            result['user_has_paid'] = user_paid
        
        return result
    
# Add this to the existing serializers.py file

class EventWithPaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating an event with payment information
    """
    payment_link = serializers.URLField(required=False, allow_null=True)
    payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    payment_description = serializers.CharField(max_length=255, required=False, allow_null=True)
    
    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'date', 'location', 
            'privacy', 'cover_image', 'latitude', 'longitude',
            'payment_link', 'payment_amount', 'payment_description'
        )
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        # Extract payment data
        payment_link = validated_data.pop('payment_link', None)
        payment_amount = validated_data.pop('payment_amount', None)
        payment_description = validated_data.pop('payment_description', None)
        
        # Set the current user as the creator
        validated_data['created_by'] = self.context['request'].user
        
        # Create the event
        event = super().create(validated_data)
        
        # Create payment if link is provided
        if payment_link:
            from apps.payments.models import Payment
            
            Payment.objects.create(
                event=event,
                user=self.context['request'].user,  # Host is creating the payment link
                payment_link=payment_link,
                amount=payment_amount,
                description=payment_description,
                status='PENDING'
            )
        
        return event