# chats/permissions.py
from rest_framework import permissions
from .models import Conversation, Message

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allow access only if the requesting user is a participant of
    the conversation (for both Conversation and Message objects).
    """

    def has_permission(self, request, view):
        # User must at least be authenticated
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
