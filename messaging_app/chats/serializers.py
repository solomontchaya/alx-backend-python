from rest_framework import serializers
from .models import User, Conversation, Message, ConversationParticipant

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id', 
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'role', 
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def create(self, validated_data):
        # Handle password hashing
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        # Handle password update
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class UserBasicSerializer(serializers.ModelSerializer):
    """Simplified user serializer for nested relationships"""
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserBasicSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='sender',
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Message
        fields = [
            'message_id', 
            'sender', 
            'sender_id', 
            'conversation', 
            'message_body', 
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']
        extra_kwargs = {
            'conversation': {'required': True}
        }
    
    def create(self, validated_data):
        # Ensure the sender is the authenticated user or validated sender
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Override sender with the authenticated user for security
            validated_data['sender'] = request.user
        return super().create(validated_data)
    
class ConversationParticipantSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=True
    )
    
    class Meta:
        model = ConversationParticipant
        fields = ['user', 'user_id', 'joined_at']
        read_only_fields = ['joined_at']

class ConversationSerializer(serializers.ModelSerializer):
    participants = ConversationParticipantSerializer(
        source='conversation_participants', 
        many=True, 
        read_only=True
    )
    messages = MessageSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'messages',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        
        # Create the conversation
        conversation = Conversation.objects.create(**validated_data)
        
        # Add participants
        for user_id in participant_ids:
            try:
                user = User.objects.get(user_id=user_id)
                ConversationParticipant.objects.create(
                    conversation=conversation,
                    user=user
                )
            except User.DoesNotExist:
                # Handle non-existent user gracefully
                continue
        
        return conversation
    
    def update(self, instance, validated_data):
        # Handle participant updates if needed
        participant_ids = validated_data.pop('participant_ids', None)
        
        if participant_ids is not None:
            # Clear existing participants and add new ones
            instance.conversation_participants.all().delete()
            for user_id in participant_ids:
                try:
                    user = User.objects.get(user_id=user_id)
                    ConversationParticipant.objects.create(
                        conversation=instance,
                        user=user
                    )
                except User.DoesNotExist:
                    continue
        
        return instance

class ConversationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing conversations"""
    participants = UserBasicSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'last_message',
            'unread_count',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return {
                'message_body': last_message.message_body,
                'sent_at': last_message.sent_at,
                'sender_id': last_message.sender.user_id
            }
        return None
    
    def get_unread_count(self, obj):
        # You can implement read/unread logic here if needed
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Example: count messages after user's last read timestamp
            return 0  # Implement your actual logic
        return 0
    
class ConversationDetailSerializer(ConversationSerializer):
    """Extended serializer with full message details"""
    messages = MessageSerializer(many=True, read_only=True)
    participants = UserBasicSerializer(
        many=True,
        read_only=True,
        source='conversation_participants.user'
    )
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'messages',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

class CreateMessageSerializer(serializers.ModelSerializer):
    """Serializer specifically for creating messages"""
    class Meta:
        model = Message
        fields = ['conversation', 'message_body']
        extra_kwargs = {
            'conversation': {'required': True},
            'message_body': {'required': True}
        }
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['sender'] = request.user
        return super().create(validated_data)

class AddParticipantSerializer(serializers.Serializer):
    """Serializer for adding participants to a conversation"""
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True
    )
    
    def validate_user_ids(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("At least one user ID is required.")
        return value