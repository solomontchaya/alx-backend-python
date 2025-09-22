from rest_framework import serializers
from .models import User, Conversation, Message

# -----------------------
# User Serializer
# -----------------------
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)  # CharField example

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'full_name', 'email', 'phone_number', 'role', 'created_at']


# -----------------------
# Message Serializer
# -----------------------
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'message_body', 'sent_at']


# -----------------------
# Conversation Serializer with nested messages
# -----------------------
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()  # Explicit SerializerMethodField

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']

    # Populate messages in nested format
    def get_messages(self, obj):
        messages = obj.messages.all().order_by('sent_at')
        return MessageSerializer(messages, many=True).data

    # Example validation: ensure at least 2 participants
    def validate(self, data):
        if self.instance:
            participants_count = self.instance.participants.count()
        else:
            participants_count = len(self.initial_data.get('participants', []))
        if participants_count < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants.")
        return data
