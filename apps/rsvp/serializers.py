from rest_framework import serializers
from .models import RSVP
from apps.users.serializers import UserSerializer
from apps.events.serializers import EventSerializer

class RSVPSerializer(serializers.ModelSerializer):
    """
    Serializer for the RSVP model (list view)
    """
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    payment_status = serializers.SerializerMethodField()
    
    class Meta:
        model = RSVP
        fields = (
            'id', 'event', 'user', 'status', 
            'plus_ones', 'is_approved','payment_status',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_payment_status(self, obj):
        # Only include payment status for the event host or the RSVP owner
        user = self.context['request'].user
        if user == obj.event.created_by or user == obj.user:
            return obj.payment_status
        return None

class RSVPCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new RSVP
    """
    event_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = RSVP
        fields = ('id', 'event_id', 'status', 'plus_ones')
        read_only_fields = ('id',)
    
    def validate(self, data):
        """
        Check that the user is not already RSVP'd to this event
        Also sets the is_approved flag based on event privacy
        """
        event_id = data['event_id']
        user = self.context['request'].user
        
        from apps.events.models import Event
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event does not exist")
        
        # Check if the user already has an RSVP for this event
        if RSVP.objects.filter(event_id=event_id, user=user).exists():
            raise serializers.ValidationError("You have already RSVP'd to this event")
        
        # For private events, set is_approved to False initially (host must approve)
        data['is_approved'] = event.privacy != 'PRIVATE'
        
        # Save the event for create method
        self.event = event
        
        return data
    
    def create(self, validated_data):
        event_id = validated_data.pop('event_id')
        user = self.context['request'].user
        
        # Create the RSVP
        rsvp = RSVP.objects.create(
            event_id=event_id,
            user=user,
            **validated_data
        )
        
        return rsvp

class RSVPUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an RSVP
    """
    class Meta:
        model = RSVP
        fields = ('status', 'plus_ones')

class RSVPApprovalSerializer(serializers.ModelSerializer):
    """
    Serializer for approving/rejecting an RSVP
    """
    class Meta:
        model = RSVP
        fields = ('is_approved',)

class GuestListSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying guest list
    """
    user = UserSerializer()
    
    class Meta:
        model = RSVP
        fields = ('id', 'user', 'status', 'plus_ones', 'is_approved')