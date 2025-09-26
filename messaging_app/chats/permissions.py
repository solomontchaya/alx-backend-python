# chats/permissions.py
from rest_framework import permissions
from .models import Conversation, Message

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allow only authenticated participants of a conversation to
    access or modify that conversation or its messages.
    """

    def has_permission(self, request, view):
        # Must be authenticated to even access the endpoint
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # obj can be a Conversation or a Message
        if isinstance(obj, Message):
            conversation = obj.conversation
        elif isinstance(obj, Conversation):
            conversation = obj
        else:
            return False
        return conversation.participants.filter(id=request.user.id).exists()
