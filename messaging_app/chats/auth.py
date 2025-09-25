# messaging_app/chats/auth.py
from rest_framework import permissions
from .models import Conversation, Message

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow:
    - Only authenticated users
    - Only participants of a conversation to read or write messages
    """

    def has_permission(self, request, view):
        # Step 1: User must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        `obj` can be either a Message or a Conversation instance depending on the viewset.
        We check if the logged-in user is one of the conversation participants.
        """
        if isinstance(obj, Message):
            conversation = obj.conversation
        elif isinstance(obj, Conversation):
            conversation = obj
        else:
            return False

        return conversation.participants.filter(id=request.user.id).exists()
