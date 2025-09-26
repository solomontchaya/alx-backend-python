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
        """
        Extra explicit control:
        - GET, HEAD, OPTIONS: allow if user is a participant
        - PUT, PATCH, DELETE: allow if user is a participant (explicitly listed)
        """
        if isinstance(obj, Message):
            conversation = obj.conversation
        elif isinstance(obj, Conversation):
            conversation = obj
        else:
            return False

        is_participant = conversation.participants.filter(id=request.user.id).exists()

        # Explicitly handle unsafe methods
        if request.method in ['PUT', 'PATCH', 'DELETE', 'POST']:
            return is_participant  # participant required for create/update/delete

        # Safe methods (GET/HEAD/OPTIONS) also require participant
        if request.method in permissions.SAFE_METHODS:
            return is_participant

        # Default to participant check for any other methods
        return is_participant
