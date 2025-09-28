# chats/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsParticipantOfConversation(BasePermission):
    """
    Custom permission:
    - Only authenticated users can access the API
    - Only participants of a conversation can create, view, update, or delete messages
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        obj may be a Conversation or Message.
        """
        # Restrict to allowed methods
        if request.method not in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            return False

        if hasattr(obj, "participants"):  # Conversation
            return request.user in obj.participants.all()

        if hasattr(obj, "conversation"):  # Message
            return request.user in obj.conversation.participants.all()

        return False
